from django.db import models


# Create your models here.
class StockPredictorModel(models.Model):
    name = models.CharField(max_length=50, unique=True)
    stock_type = models.CharField(max_length=20)
    predict_type = models.CharField(max_length=20)
    job_path = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class PredictHistModel(models.Model):
    predict_model = models.ForeignKey(StockPredictorModel, on_delete=models.CASCADE, related_name='predict_hists')
    vol_moving_avg = models.BigIntegerField(null=True, blank=True)
    price_rolling_med = models.FloatField(null=True, blank=True)
    price_daily_std = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
