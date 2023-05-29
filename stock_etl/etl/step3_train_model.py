import joblib
import os
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import mutual_info_regression
# from sklearn import tree

# import matplotlib.pyplot as plt
# import seaborn as sns
RADOM_STATE = 188


class StockPredictor:
    def __init__(self, n_estimators, random_state):
        print('StockPredictor.__init__', n_estimators, random_state)
        self.fs = None
        self.model_fit = False
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)

    def select_features(self, X_train, y_train, column_names, num_features):
        if num_features > len(column_names) or num_features <= 0:
            return

        # configure to select a subset of features
        self.fs = SelectKBest(score_func=mutual_info_regression, k=num_features)
        self.fs.fit(X_train, y_train)
        return self.fs.get_feature_names_out(column_names)

    def fit(self, X_train, y_train):
        self.model_fit = True
        if self.fs is None:
            self.model.fit(X_train, y_train)
        else:
            # transform the train data into best features
            best_features = self.fs.transform(X_train)
            print(f'best features: {best_features[:3]}')
            self.model.fit(best_features, y_train)

    def predict(self, X_data):
        if not self.model_fit:
            return

        if self.fs is None:
            return self.model.predict(X_data)
        else:
            # transform the train data into best features
            best_features = self.fs.transform(X_data)
            print(f'best features: {best_features[:3]}')
            return self.model.predict(best_features)


def main(model_output, staging_data_path, predictors):
    # Load the staging parquet
    data_df = pd.read_parquet(staging_data_path)
    #
    # Assume `data` is loaded as a Pandas DataFrame
    data_df['Date'] = pd.to_datetime(data_df['Date'])
    data_df.set_index('Date', inplace=True)

    # Remove rows with NaN values
    data_df.dropna(inplace=True)

    if 'adj_close_rolling_med' in data_df.columns:
        # Remove the adj_close_rolling_med with negative or big numbers
        selected_price = ((data_df['adj_close_rolling_med'] > 0) & (data_df['adj_close_rolling_med'] < 1000000))
        data_df = data_df[selected_price]

    for config_dict in predictors:
        predict_model_path = f'{model_output}_{config_dict["Target_Name"]}_Model.joblib'
        feat_columns = config_dict['Target_Features']
        num_features = config_dict.get('Num_Features')
        n_estimators = config_dict.get('N_Estimators', 40)

        build_predict_model(predict_model_path, data_df, feat_columns, num_features, n_estimators)


def build_predict_model(predict_model_path, data_df, feat_columns, num_features, n_estimators):
    print(f'feat_columns: {len(feat_columns)} - {feat_columns}')
    price_df = data_df[feat_columns].sample(n=3000, random_state=RADOM_STATE)
    desc_df = price_df.describe().reset_index()
    print(desc_df)
    train_columns = feat_columns[1:]
    target = feat_columns[0]

    X = data_df[train_columns].to_numpy()
    y = data_df[target].to_numpy()
    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RADOM_STATE)
    print(f'Split the train data: {len(X_train)} - test data: {len(X_test)}')

    # Define the StockPredictor
    # # Create a RandomForest Regressoion model
    stock_predictor = RandomForestRegressor(n_estimators=n_estimators, random_state=RADOM_STATE)
    # stock_predictor, best_features = select_best_features(X_train, y_train, train_columns, num_features, n_estimators)

    # Descriptive statistics for each column
    pd.set_option('display.float_format', lambda x: '%.3f' % x)

    # Train the model
    stock_predictor.fit(X_train, y_train)
    # Save the model
    joblib.dump(stock_predictor, predict_model_path)
    print('Save the regression model:', predict_model_path)

    # Load the model
    loaded_model = joblib.load(predict_model_path)
    print('Load the regression model:', predict_model_path)

    # Calculate and display accuracy
    train_output = [
        f'Model: {predict_model_path}',
        f'Train data: {len(X_train)}',
        f'Test data: {len(X_test)}',
        f'Target: {target}',
        f'Train Features: {train_columns}',
    ]

    # if best_features is not None:
    #     train_output.append(f'Best Features: {best_features}')

    # Make predictions on test data
    y_pred = loaded_model.predict(X_test)
    if y_pred is not None:
        # Calculate the Mean Absolute Error and Mean Squared Error
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        train_output.extend([
            f'Mean Absolute Error: {mae}',
            f'Mean Squared Error: {mse}',
            f'Root Mean Squared Error: {np.sqrt(mse)}',
        ])

    print('Train metrics:', train_output)
    output_df = pd.DataFrame({'Metrics': train_output})
    metrix_dict = {
        'Train metrics': output_df, 'Train Data': desc_df,
    }

    # Obtain the first regression tree
    # tree_text = tree.export_text(loaded_model.estimators_[0], feature_names=features, max_depth=20)
    # Save the training metrics
    logs_output = predict_model_path.replace('.joblib', '_Metrics.txt')
    export_model_training_result(logs_output, metrix_dict)


def select_best_features(X_train, y_train, train_columns, num_features, n_estimators):
    stock_predictor = StockPredictor(n_estimators, RADOM_STATE)
    # Select features and target
    best_features = stock_predictor.select_features(X_train, y_train, train_columns, num_features)
    print(f'Target: Select features: {len(best_features)} - {best_features}')
    return stock_predictor, best_features


def export_model_training_result(logs_output, metrix_dict):
    with open(logs_output, "a") as fp:
        # Write the model result
        for key, df in metrix_dict.items():
            fp.write(f"\n\n{key} Summary\n{'-'*50}\n")
            if key == 'Train Data':
                header = True
            else:
                header = False
            output_text = df.to_string(header=header, index=False)
            fp.write(output_text)

        # Write the Tree
        # fp.write(f"\n\nRegression Tree:\n{'-' * 60}\n{tree_text}\n\n\n")
    print('Write the regression model output:', logs_output)
