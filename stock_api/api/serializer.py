from rest_framework import serializers
from .models import StockPredictorModel, StockVolumeModel


class StockPredictorSerializer(serializers.ModelSerializer):
  class Meta:
    model= StockPredictorModel
    fields = ['name']


class StockVolumeSerializer(serializers.ModelSerializer):
  class Meta:
    model= StockVolumeModel
    fields = ['predict_model', 'vol_moving_avg', 'price_rolling_med', 'predict_volume']
