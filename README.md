# Work Sample for Data Engineer

To effectively solve the following data pipeline problems, it is essential to use a DAG (Directed Acyclic Graph) oriented tool. DAG tools like Pachyderm, Airflow, Dagster, etc., can help streamline data processing and management with tracking data lineage, ensuring data integrity, and minimizing errors during processing.

To provide more context and clarity, including pipeline specs and diagrams can be helpful. These artifacts can help visualize the DAG and its components, provide information on how data flows through the pipeline, and highlight the dependencies between tasks.

## Problem 1: Raw Data Processing

**Objective**: Ingest and process raw stock market datasets.

### Tasks:
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

## Problem 2: Feature Engineering

**Objective**: Build some feature engineering on top of the dataset from Problem 1.

### Tasks:
1. Calculate the moving average of the trading volume (`Volume`) of 30 days per each stock and ETF, and retain it in a newly added column `vol_moving_avg`.
2. Similarly, calculate the rolling median and retain it in a newly added column `adj_close_rolling_med`.
3. Retain the resulting dataset into the same format as Problem 1, but in its own stage/directory distinct from the first.
4. (Bonus) Write unit tests for any relevant logic.

## Problem 3: Integrate ML Training

**Objective**: Integrate an ML predictive model training step into the data pipeline.

You can use the following simple Random Forest model as a reference:

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Assume `data` is loaded as a Pandas DataFrame
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Remove rows with NaN values
data.dropna(inplace=True)

# Select features and target
features = ['vol_moving_avg', 'adj_close_rolling_med']
target = 'Volume'

X = data[features]
y = data[target]

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a RandomForestRegressor model
model = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the model
model.fit(X_train, y_train)

# Make predictions on test data
y_pred = model.predict(X_test)

# Calculate the Mean Absolute Error and Mean Squared Error
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
```

You may come up with your own process with any choice of model architectures, algorithms, libraries, and training configurations.

### Tasks:
1. Integrate the ML training process as a part of the data pipeline.
2. Save the resulting model to disk.
3. Persist any training metrics, such as loss and error values as log files.
4. (Bonus) If you choose your own model implementation, articulate why it's better as a part of your submission.

## Problem 4: Model Serving

**Objective**: Build an API service to serve the trained predictive model.

### Tasks:
1. Implement an API service to serve the trained predictive model.
2. An `/predict` API endpoint which takes two values, `vol_moving_avg` and `adj_close_rolling_med`, and responds with an integer value that represents the trading volume.
    ```shell
    # hypothetical HTTP GET request and response
    GET /predict?vol_moving_avg=12345&adj_close_rolling_med=25
    -> 10350
    ```
3. (Bonus) Test the API service, document your methodology, provisioned computing resources, test results, a breakdown of observable bottlenecks (e.g. model loading/inference, socket/IO, etc.), and improvement suggestions for hypothetical future iterations.


# Stock Predict API

### Pre-requisities:
Docker

### Step 0: Download the repo

Create a copy of `.env` file with `cp env_sample .env`, and set the environment variables to your desired values. `.env` is used by `docker-compose` for retrieving sensitive information such as password.

### Step 1: Build docker images
```sh
$ docker-compose build
```

### Step 2: Parameter Configuration
Create a copy of `stock_data/input/stock_config.json` file with `cp stock_sample.json stock_data/input/stock_config.json`, and set the ETL configures to your desired values. 

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

### Step 3: Usage

To run the Stock ETL job to generate two predict models for Stocks and ETFs, for example, run the following on the Terminal:
```sh
docker-compose up stock_etl
```

To run the Stock Predict API, for example, run the following on the Terminal:
```sh
docker-compose up db stock_api
```

To test the Stock Predict API using httpie. for example, run the following on the Terminal:
```sh
http POST http://127.0.0.1:8000/api/stock/volumes/ vol_moving_avg=12345 price_rolling_med:=25

HTTP/1.1 201 Created
Allow: GET, POST, HEAD, OPTIONS
Content-Length: 92
Content-Type: application/json
Date: Sat, 20 May 2023 20:16:54 GMT
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.9.16
Vary: Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{
    "predict_model": 2,
    "predict_volume": 11785.0,
    "price_rolling_med": 25.0,
    "vol_moving_avg": 12345
}
```

```sh
http POST http://127.0.0.1:8000/api/etf/volumes/ vol_moving_avg=12345 price_rolling_med:=25

HTTP/1.1 201 Created
Allow: GET, POST, HEAD, OPTIONS
Content-Length: 92
Content-Type: application/json
Date: Sat, 20 May 2023 20:17:28 GMT
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.9.16
Vary: Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
{
    "predict_model": 1,
    "predict_volume": 19990.0,
    "price_rolling_med": 25.0,
    "vol_moving_avg": 12345
}
```
