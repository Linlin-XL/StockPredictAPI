import joblib
import os
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn import tree

# import matplotlib.pyplot as plt
# import seaborn as sns


def main(joblib_stock_model_path, staging_data_path):
    # Load the staging parquet
    data_df = pd.read_parquet(staging_data_path)

    # Assume `data` is loaded as a Pandas DataFrame
    data_df['Date'] = pd.to_datetime(data_df['Date'])
    data_df.set_index('Date', inplace=True)

    # Remove rows with NaN values
    data_df.dropna(inplace=True)

    # Remove the adj_close_rolling_med with negative or big numbers
    selected_price = ((data_df['adj_close_rolling_med'] > 0) & (data_df['adj_close_rolling_med'] < 1000000))
    data_df = data_df[selected_price]

    # Select features and target
    features = ['vol_moving_avg', 'adj_close_rolling_med']
    target = 'Volume'

    # Descriptive statistics for each column
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    desc_df = data_df[['vol_moving_avg', 'adj_close_rolling_med', 'Volume']].describe().reset_index()
    print(desc_df)

    X = data_df[features]
    y = data_df[target]

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f'Split the train data: {len(X_train)} - test data: {len(X_test)}')

    # Create a RandomForest Regressor model
    model = RandomForestRegressor(n_estimators=80, random_state=42)

    # Train the model
    model.fit(X_train, y_train)

    # Save the model
    joblib.dump(model, joblib_stock_model_path, compress=6)
    print('Save the regression model:', joblib_stock_model_path)

    # Load the model
    loaded_model = joblib.load(joblib_stock_model_path)
    print('Load the regression model:', joblib_stock_model_path)

    # Make predictions on test data
    y_pred = loaded_model.predict(X_test)

    # Calculate the Mean Absolute Error and Mean Squared Error
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    # Calculate and display accuracy
    train_output = [
        f'Model: {joblib_stock_model_path}',
        f'Train data: {len(X_train)}',
        f'Test data: {len(X_test)}',
        f'Mean Absolute Error: {mae}',
        f'Mean Squared Error: {mse}',
        f'Root Mean Squared Error: {np.sqrt(mse)}',
    ]

    print('Train metrics:', train_output)
    output_df = pd.DataFrame([[i] for i in train_output], columns=['Metrics'])
    output_dict = {
        'Train metrics': output_df, 'Train Data': desc_df,
    }

    # Obtain the first regression tree
    tree_text = tree.export_text(loaded_model.estimators_[0], feature_names=features, max_depth=20)

    # Save the training metrics
    logs_output = joblib_stock_model_path.replace('.joblib', '_Metrics.txt')
    export_model_training_result(logs_output, output_dict, tree_text)


def export_model_training_result(logs_output, train_dict, tree_text):
    with open(logs_output, "a") as fp:
        # Write the model result
        for key, df in train_dict.items():
            fp.write(f"\n\n{key} Summary\n{'-'*60}\n")
            if key == 'Train Data':
                header = True
            else:
                header = False
            output_text = df.to_string(header=header, index=False)
            fp.write(output_text)

        # Write the Tree
        fp.write(f"\n\nRegression Tree:\n{'-' * 60}\n{tree_text}\n\n\n")
    print('Write the regression model output:', logs_output)
