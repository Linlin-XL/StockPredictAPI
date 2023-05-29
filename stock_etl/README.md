# Stock Data ETL Pipeline

### Parameter Configuration
A sample configure in `stock-config.json` looks like this:
```json
{
  "Model_Name": "StockPredict_v1_2019",
  "Output_Data": "stock_data/output_data",
  "Output_Model": "stock_data/output_model",
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
  ],  
  "Predictors": [
    {
      "Target_Name": "Volume",
      "Target_Features": ["future_volume", "vol_moving_avg", "adj_close_rolling_med"]
    }
  ]
}
```

### Usage

To get usage instructions, for example, run the following on the Terminal:
```sh
python etl_task.py -h
```

This will output:
```text
usage: etl_task.py [-h] [-stock STOCK_CONF] [-spark SPARK_CONF]

Stock Data ETL Pipeline

optional arguments:
  -h, --help            show this help message and exit
  -stock STOCK_CONF, --stock_conf STOCK_CONF
                        path to stock data configuration file: 
                        {
                          "Model_Name": "StockPredict_v1_2019",
                          "Output_Data": "stock_data/output_data",
                          "Output_Model": "stock_data/output_model",
                          "Stock_Desc": "stock_data/input/symbols_valid_meta.csv",
                          "Stock_Data": {
                            "Stock": "stock_data/input/stocks",
                            "ETF": "stock_data/input/etfs"
                          },
                          "Start_Date": "2019-01-01",
                          "ETL_Steps": ["Step1", "Step2", "Step3"],  
                          "Predictors": [
                            {
                              "Target_Name": "Volume",
                              "Target_Features": ["future_volume", "vol_moving_avg", "adj_close_rolling_med"]
                            }
                          ]
                        }
  -spark SPARK_CONF, --spark_conf SPARK_CONF
                        path to Spark configuration file
```

Based on the usage, the script can be executed by providing the path to configuration JSON file as
```sh
python etl_task.py -stock stock-config.json
```
