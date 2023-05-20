import logging
import os

import pyspark.sql.functions as F
from pyspark.sql.types import StringType, FloatType, IntegerType, TimestampType
from pyspark.sql.types import StructType, StructField
from pyspark.sql.utils import ParseException

from etl.spark.udf import get_symbol_filename_udf

logger = logging.getLogger(__name__)


def main(spark, stock_csv, symbol_csv, start_date, end_date, data_output_path):
    schema = StructType([
        StructField("Date", StringType()),
        StructField("Open", FloatType()),
        StructField("High", FloatType()),
        StructField("Low", FloatType()),
        StructField("Close", FloatType()),
        StructField("Adj Close", FloatType()),
        StructField("Volume", IntegerType())
    ])

    try:
        df_daily = spark.read.csv(stock_csv, schema=schema, sep=',', header=True)
    except ParseException as e:
        logger.error(str(e))
        raise e

    df_daily = df_daily.withColumn('Symbol', get_symbol_filename_udf(F.input_file_name())) \
        .withColumn('Symbol', get_symbol_filename_udf(F.input_file_name())) \
        .withColumn('Date2', F.to_date('Date', 'yyyy-MM-dd'))

    df_daily.printSchema()

    df_daily.summary().show()

    date_from, date_to = [
        F.to_date(F.lit(i)).cast(TimestampType()) if i is not None else None for i in [start_date, end_date]
    ]
    if start_date is not None:
        logger.info(f'Start Date: {start_date}')
        df_daily = df_daily.filter(df_daily.Date2 >= date_from)

    if end_date is not None:
        logger.info(f'End Date: {end_date}')
        df_daily = df_daily.filter(df_daily.Date2 <= date_to)

    logger.info(df_daily.show(10))

    try:
        df_symbol = spark.read.csv(symbol_csv, sep=',', inferSchema=True, header=True)
    except ParseException as e:
        logger.error(str(e))
        raise e

    df_out = df_daily.join(df_symbol.select(['Symbol', 'Security Name']), on='Symbol', how='left')
    print(df_out.show(10))
    df_out.printSchema()

    data_dir = os.path.dirname(data_output_path)
    os.makedirs(data_dir, exist_ok=True)
    df_out.write.partitionBy('Symbol').mode('overwrite').parquet(data_output_path)
    print('Export:', data_output_path)
