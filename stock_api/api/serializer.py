from rest_framework import serializers
from .models import StockPredictorModel, PredictHistModel


class StockPredictorSerializer(serializers.ModelSerializer):
  class Meta:
    model= StockPredictorModel
    fields = ['name', 'stock_type', 'predict_type']


class PredictHistModelSerializer(serializers.ModelSerializer):
  class Meta:
    model= PredictHistModel
    fields = [
      'predict_model', 'vol_moving_avg', 'price_rolling_med', 'price_daily_std', 'volume', 'price',
    ]
