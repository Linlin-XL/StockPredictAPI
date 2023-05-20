import logging
import os
from sklearn.ensemble import RandomForestRegressor
import joblib

logger = logging.getLogger(__name__)


def predict_volume_joblib(model_path, vol_moving_avg, adj_close_rolling_med):
    # Load the model
    pred_vol_model = joblib.load(model_path)
    print(f'Load the regression model: {model_path}')

    # Make predictions
    request_data = [[vol_moving_avg, adj_close_rolling_med]]
    print(f'Request_data: {request_data}')

    y_pred = pred_vol_model.predict(request_data)
    print(f'Prediction: {y_pred}')
    return {'Volume': y_pred[0]}
