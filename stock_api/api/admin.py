from django.contrib import admin
from .models import StockPredictorModel, StockVolumeModel


# Register your models here.
admin.site.register(StockPredictorModel)

admin.site.register(StockVolumeModel)
