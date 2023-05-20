import argparse
import json
import os

from etl.spark.session import start_spark
from etl import step1_ingest_data, step2_extract_features, step3_train_model

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def start_etl_task(spark, stock_config, output_data, output_model):
    # Define the Stock ETL configure
    model_name = stock_config['Model_Name']
    symbol_csv = stock_config['Stock_Desc']
    start_date = stock_config.get('Start_Date')
    end_date = stock_config.get('End_Date')
    etl_steps = stock_config.get('ETL_Steps', ['Step1', 'Step2', 'Step3'])

    for stock_type, stock_csv in stock_config['Stock_Data'].items():
        data_ingest = os.path.join(output_data, f'{model_name}_{stock_type}_Ingest_Data')
        data_staging = os.path.join(output_data, f'{model_name}_{stock_type}_Stage_Data')
        model_joblib = os.path.join(output_model, f'{model_name}_{stock_type}_Model.joblib')

        # Step 1 - Ingest the CSV file
        if "Step1" in etl_steps:
            step1_ingest_data.main(spark, stock_csv, symbol_csv, start_date, end_date, data_ingest)

        # Step 2 - Feature Engineering
        if "Step2" in etl_steps:
            step2_extract_features.main(spark, data_ingest, data_staging)

        # Step 3 - ML Training
        if "Step3" in etl_steps:
            step3_train_model.main(model_joblib, data_staging)


def main(stock_config, spark_config=None):
    # Define the Stock ETL output path
    model_name = stock_config['Model_Name']
    output_data = os.environ.get("ETL_Data_Path", "stock_data/output_data")
    output_model = os.environ.get("ETL_Model_Path", "stock_data/output_model")
    output_missed = [
        i for i in [output_data, output_model] if not os.path.exists(i)
    ]
    if len(output_missed) > 0:
        raise ValueError(f'Output path {", ".join(output_missed)} does not exist.')

    if 'Step1' in stock_config['ETL_Steps'] or 'Step2' in stock_config['ETL_Steps']:
        spark = start_spark(model_name, spark_config)
    else:
        spark = None

    try:
        start_etl_task(spark, stock_config, output_data, output_model)
        print(f'stock_config: {stock_config}')
        print(f'output_data: {output_data}')
        print(f'output_model: {output_model}')
    finally:
        if spark is not None:
            spark.stop()


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='Stock Data ETL Task')
    conf_sample = """
    {
      "Model_Name": "Predict_Volume_2019_v1",
      "Stock_Desc": "stock_data/input/symbols_valid_meta.csv",
      "Stock_Data": {
        "Stock": "stock_data/input/stocks",
        "ETF": "stock_data/input/etfs"
      },
      "Start_Date": "2019-01-01",
      "ETL_Steps": ["Step1", "Step2", "Step3"]
    }
    """
    cli_parser.add_argument(
        '-stock', '--stock_conf', dest='stock_conf',
        type=argparse.FileType('r'), default=None,
        help=f'path to stock data configuration file: {conf_sample}',
    )

    cli_parser.add_argument(
        '-spark', '--spark_conf', dest='spark_conf',
        type=argparse.FileType('r'), default=None,
        help=f'path to Spark configuration file',
    )

    args = cli_parser.parse_args()

    # Load the JSON config file
    if args.stock_conf is not None:
        stock_conf = json.load(args.stock_conf)
    else:
        stock_env = os.getenv('Stock_Config', 'stock_data/input/stock_config.json')
        if not os.path.exists(stock_env):
            raise ValueError(f'Stock config ({stock_env}) does not exists.')
        with open(stock_env) as fp:
            stock_conf = json.load(fp)

    required_keys = [i for i in ['Model_Name', 'Stock_Desc', 'Stock_Data'] if i not in stock_conf]
    if len(required_keys) > 0:
        raise cli_parser.error(f"Missing configure {', '.join(required_keys)} in {args.config_file.name}")

    if args.spark_conf is not None:
        spark_conf = json.load(args.spark_conf)
    else:
        spark_env = os.getenv('Spark_Config', 'stock_data/input/spark_config.json')
        if os.path.exists(spark_env):
            with open(spark_env) as fp:
                spark_conf = json.load(fp)
        else:
            spark_conf = None

    print(f'stock_conf: {stock_conf}')
    print(f'spark_conf: {spark_conf}')
    main(stock_conf, spark_conf)
