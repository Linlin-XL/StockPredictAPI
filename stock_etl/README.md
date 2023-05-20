# Stock Data ETL Pipeline

### Parameter Configuration
A sample configure in `stock_config.json` looks like this:
```json
{
  "Model_Name": "Predict_Volume_2019_v1",
  "Stock_Desc": "stock_data/input/symbols_valid_meta.csv",
  "Stock_Data": {
    "Stock": "stock_data/input/stocks",
    "ETF": "stock_data/input/etfs"
  },
  "Start_Date": "2019-01-01",
  "ETL_Steps": [
    "Step1",
    "Step2",
    "Step3"
  ]
}
```

### Usage

To get usage instructions, for example, run the following on the Terminal:
```sh
python stock_etl.py -h
```

This will output:
```text
usage: stock_etl.py [-h] -stock STOCK_CONF [-spark SPARK_CONF]

Stock Data ETL Pipeline

optional arguments:
  -h, --help            show this help message and exit
  -stock STOCK_CONF, --stock_conf STOCK_CONF
                        path to stock data configuration file: 
                        {
                            "Model_Name": "Predict_Volume_v01_2018", 
                            "Stock_Desc": "data/input/symbols_valid_meta.csv", 
                            "Stock_Data": { "Stock": "data/input/stocks", "ETF": "data/input/etfs" }, 
                            "Start_Date": "2018-01-01", 
                            "ETL_Steps": ["Step1", "Step2", "Step3"]
                        }
  -spark SPARK_CONF, --spark_conf SPARK_CONF
                        path to Spark configuration file
```

Based on the usage, the script can be executed by providing the path to configuration JSON file as
```sh
python stock_etl.py -stock stock_config.json
```
