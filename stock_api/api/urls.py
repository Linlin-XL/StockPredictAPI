# api/urls.py

from django.urls import path

from . import views

urlpatterns = [
    path('csrf/', views.get_csrf, name='api-csrf'),
    path('login/', views.login_view, name='api-login'),
    path('logout/', views.logout_view, name='api-logout'),
    path('session/', views.SessionView.as_view(), name='api-session'),
    path('whoami/', views.WhoAmIView.as_view(), name='api-whoami'),
    path('predictors/', views.PredictorList.as_view()),
    path('predictors/detail/<int:pk>/', views.PredictorDetail.as_view()),
    path('stock/volumes/', views.PredictStockVolumeList.as_view()),
    path('etf/volumes/', views.PredictETFVolumeList.as_view()),
    path('volumes/detail/<int:pk>/', views.PredictVolumeDetail.as_view()),
]
