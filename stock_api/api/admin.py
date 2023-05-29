from django.contrib import admin
from .models import StockPredictorModel, PredictHistModel


# Register your models here.
admin.site.register(StockPredictorModel)

admin.site.register(PredictHistModel)
