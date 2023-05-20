from django.db import models


# Create your models here.
class StockPredictorModel(models.Model):
    name = models.CharField(max_length=50, unique=True)
    job_path = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class StockVolumeModel(models.Model):
    predict_model = models.ForeignKey(StockPredictorModel, on_delete=models.CASCADE, related_name='stock_volumes')
    vol_moving_avg = models.BigIntegerField()
    price_rolling_med = models.FloatField()
    predict_volume = models.FloatField()
