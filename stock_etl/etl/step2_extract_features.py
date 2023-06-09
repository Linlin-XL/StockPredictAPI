import logging
import math
import os
import sys
from pyspark.sql.window import Window
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType
from etl.spark.udf import get_number_sign_udf, get_market_trend_udf

logger = logging.getLogger(__name__)


def main(spark, stock_price_daily, stock_price_staging, start_date, end_date):
    try:
        df_daily = spark.read.parquet(stock_price_daily)
    except Exception as e:
        logger.warning(f'file {stock_price_daily} does not exists!')
        raise e

    df_daily.printSchema()

    # we need this timestampGMT as seconds for our Window time frame
    # df_daily = df_daily.withColumn('TimeStamp', F.unix_timestamp(F.to_timestamp('Date')).cast('long'))
    df_daily = df_daily.withColumn('TimeStamp', F.unix_timestamp('Date2').cast('long'))

    # Total seconds of selected days
    days = lambda i: i * 86400

    # 252 - number of trading days in a year
    annual_rate = math.sqrt(252)

    # we need this timestampGMT as seconds for our Window time frame
    # Define the window partition by Symbol order by TimeStamp
    symbol_partition = Window.partitionBy('Symbol').orderBy(F.col("TimeStamp"))

    # Rolling window of 30 days per each stock and ETF
    symbol_30days_win = symbol_partition.rangeBetween(-days(30), 0)

    # Backward rolling window of maximum size per each stock and ETF
    symbol_backward_win = symbol_partition.rowsBetween(-sys.maxsize, 0)

    def get_median(col_name, win):
        """Calculate the median value over the rolling window"""
        return F.percentile_approx(col_name, 0.5).over(win)

    def get_avg(col_name, win):
        """Calculate the mean value over the rolling window"""
        return F.avg(col_name).over(win)

    def get_daily_return(col_name, win):
        """Calculate the stock price return value"""
        return F.col(col_name) / F.lag(col_name).over(win) - F.lit(1)

    def get_std(col_name, win):
        """Calculate the sample standard deviation value over the rolling window"""
        return F.stddev_samp(col_name).over(win)

    def get_annual_std(col_name):
        """Calculate the annualized standard deviation value"""
        return F.col(col_name) * F.lit(annual_rate)

    def get_price_volume_ration(col_price, col_volume):
        """Calculate the radio of High price and Volume"""
        return F.col(col_price) / F.col(col_volume)

    def get_trend_sign(col_name, win):
        """Calculate the trend sign: +1, -1 or None"""
        return get_number_sign_udf(F.col(col_name) - F.lag(col_name).over(win))

    def get_lead_value(col_name, win):
        """Forward filled value over the rolling windows"""
        return F.lead(col_name).over(win)

    def get_backward_filled(col_name, win):
        """Backward filled value over the rolling windows"""
        return F.last(col_name, ignorenulls=True).over(win)

    # Extract the features
    df_daily = df_daily.withColumn('vol_moving_avg', get_avg('Volume', symbol_30days_win)) \
        .withColumn('vol_moving_avg_log', F.log('vol_moving_avg')) \
        .withColumn('adj_close_rolling_med', get_median('Adj Close', symbol_30days_win)) \
        .withColumn('adj_close_return', get_daily_return('Adj Close', symbol_partition)) \
        .withColumn('adj_close_daily_std', get_std('adj_close_return', symbol_30days_win)) \
        .withColumn('adj_close_annual_std', get_annual_std('adj_close_daily_std')) \
        .withColumn('adj_close_trend_flag', get_number_sign_udf(F.col('adj_close_return'))) \
        .withColumn('high_vol_ratio', get_price_volume_ration('High', 'Volume')) \
        .withColumn('vol_trend_flag', get_trend_sign('Volume', symbol_partition)) \
        .withColumn('market_trend', get_market_trend_udf(F.col('adj_close_trend_flag'), F.col('vol_trend_flag'))) \
        .withColumn('market_trend', get_backward_filled('market_trend', symbol_backward_win)) \
        .withColumn('future_adj_close', get_lead_value('Adj Close', symbol_partition)) \
        .withColumn('future_volume', get_lead_value('Volume', symbol_partition)) \
        .withColumn('future_volume_log', F.log('future_volume'))

    columns = [
        'Symbol', "Date", 'Volume', 'vol_moving_avg', 'vol_moving_avg_log', 'future_volume', 'future_volume_log',
        'Adj Close', 'adj_close_rolling_med', 'adj_close_return', 'adj_close_daily_std', 'future_adj_close',
        'market_trend', 'adj_close_trend_flag', 'vol_trend_flag',
    ]

    logger.info(f'Start Date: {start_date} - End Date: {end_date}')
    date_from, date_to = [
        F.to_date(F.lit(i)).cast(TimestampType()) if i is not None else None for i in [start_date, end_date]
    ]
    if start_date is not None:
        df_daily = df_daily.filter(df_daily.TimeStamp >= F.unix_timestamp(date_from))

    if end_date is not None:
        df_daily = df_daily.filter(df_daily.TimeStamp <= F.unix_timestamp(date_to))

    df_daily.select(columns).show(20)
    df_daily = df_daily.drop('TimeStamp')

    data_dir = os.path.dirname(stock_price_staging)
    os.makedirs(data_dir, exist_ok=True)
    df_daily.write.partitionBy('Symbol').mode("overwrite").parquet(stock_price_staging)
