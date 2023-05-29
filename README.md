# Stock Predict API

## Pre-requisities:
Docker

## Step 0: Download the repo

Create a copy of `.env` file with `cp env_sample .env`, and set the environment variables to your desired values. `.env` is used by `docker-compose` for retrieving sensitive information such as password.

## Step 1: Build docker images
```sh
$ docker-compose build
```

## Step 2: Parameter Configuration
Create a copy of `stock_data/input/stock-config.json` file with `cp stock-sample.json stock_data/input/stock-config.json`, and set the ETL configures to your desired values. 

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
    },
    {
      "Target_Name": "Price",
      "Target_Features": [
        "future_adj_close", "vol_moving_avg", "adj_close_rolling_med", "adj_close_daily_std"
      ]
    }
  ]
}
```

## Step 3: Usage

To run the Stock ETL job to generate two predict models for Stocks and ETFs, for example, run the following on the Terminal:
```sh
docker-compose up stock_etl
```

To run the Stock Predict API, for example, run the following on the Terminal:
```sh
docker-compose up db stock_api
```

To test the Stock predicted volume using httpie:
```sh
http POST http://127.0.0.1:8000/api/predict/Stock/Volume/ vol_moving_avg=12345 price_rolling_med:=25
```

To test the Stock predicted price using httpie:
```sh
http POST http://127.0.0.1:8000/api/predict/Stock/Price/ vol_moving_avg=12345 price_rolling_med:=25 price_daily_std:=0.021
```

To test the ETF predicted volume using httpie:
```sh
http POST http://127.0.0.1:8000/api/predict/ETF/Volume/ vol_moving_avg=12345 price_rolling_med:=25
```
To test the ETF predicted price using httpie:
```sh
http POST http://127.0.0.1:8000/api/predict/ETF/Price/ vol_moving_avg=12345 price_rolling_med:=25 price_daily_std:=0.021
```

## Work Sample for Data Engineer

To effectively solve the following data pipeline problems, it is essential to use a DAG (Directed Acyclic Graph) oriented tool. DAG tools like Pachyderm, Airflow, Dagster, etc., can help streamline data processing and management with tracking data lineage, ensuring data integrity, and minimizing errors during processing.

To provide more context and clarity, including pipeline specs and diagrams can be helpful. These artifacts can help visualize the DAG and its components, provide information on how data flows through the pipeline, and highlight the dependencies between tasks.

### Problem 1: Raw Data Processing

**Objective**: Ingest and process raw stock market datasets.

#### Tasks:
1. Download the ETF and stock datasets from the primary dataset available at https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset.
2. Setup a data structure to retain all data from ETFs and stocks with the following columns.
    ```
    Symbol: string
    Security Name: string
    Date: string (YYYY-MM-DD)
    Open: float
    High: float
    Low: float
    Close: float
    Adj Close: float
    Volume: int
    ```
3. Convert the resulting dataset into a structured format (e.g. Parquet).

### Problem 2: Feature Engineering

**Objective**: Build some feature engineering on top of the dataset from Problem 1.

#### Tasks:
1. Calculate the moving average of the trading volume (`Volume`) of 30 days per each stock and ETF, and retain it in a newly added column `vol_moving_avg`.
2. Similarly, calculate the rolling median and retain it in a newly added column `adj_close_rolling_med`.
3. Retain the resulting dataset into the same format as Problem 1, but in its own stage/directory distinct from the first.
4. (Bonus) Write unit tests for any relevant logic.

### Problem 3: Integrate ML Training

**Objective**: Integrate an ML predictive model training step into the data pipeline.

You may come up with your own process with any choice of model architectures, algorithms, libraries, and training configurations.

#### Tasks:
1. Integrate the ML training process as a part of the data pipeline.
2. Save the resulting model to disk.
3. Persist any training metrics, such as loss and error values as log files.
4. (Bonus) If you choose your own model implementation, articulate why it's better as a part of your submission.

### Problem 4: Model Serving

**Objective**: Build an API service to serve the trained predictive model.

#### Tasks:
1. Implement an API service to serve the trained predictive model.
2. An `/predict` API endpoint which takes two values, `vol_moving_avg` and `adj_close_rolling_med`, and responds with an integer value that represents the trading volume.
    ```shell
    # hypothetical HTTP GET request and response
    GET /predict?vol_moving_avg=12345&adj_close_rolling_med=25
    -> 10350
    ```
3. (Bonus) Test the API service, document your methodology, provisioned computing resources, test results, a breakdown of observable bottlenecks (e.g. model loading/inference, socket/IO, etc.), and improvement suggestions for hypothetical future iterations.
