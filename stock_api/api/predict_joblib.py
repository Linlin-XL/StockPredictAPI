import logging
import os
from sklearn.ensemble import RandomForestRegressor
import joblib

logger = logging.getLogger(__name__)


def predict_model_joblib(model_path, request_data):
    # Load the model
    print(f'Load the regression model: {model_path}')
    pred_model = joblib.load(model_path)

    print(f'predict data: {request_data}')
    y_pred = pred_model.predict(request_data)
    print(f'Predict: {y_pred}')
    return y_pred
