import json
import os

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse, Http404
from django.middleware.csrf import get_token
from django.views.decorators.http import require_POST
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from .models import StockPredictorModel, StockVolumeModel
from .serializer import StockVolumeSerializer, StockPredictorSerializer
from .predict_joblib import predict_volume_joblib


def get_stock_volume(pred_model, price_median, volume_average):
    if not os.path.exists(pred_model.job_path):
        return {'Error': f'Predictor path does not exist: {pred_model.job_path}'}

    result = predict_volume_joblib(pred_model.job_path, volume_average, price_median)
    return result


def get_csrf(request):
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response['X-CSRFToken'] = get_token(request)
    return response


@require_POST
def login_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    if username is None or password is None:
        return JsonResponse({'detail': 'Please provide username and password.'}, status=HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({'detail': 'Invalid credentials.'}, status=HTTP_400_BAD_REQUEST)

    login(request, user)
    return JsonResponse({'detail': 'Successfully logged in.'})


def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'You\'re not logged in.'}, status=HTTP_400_BAD_REQUEST)

    logout(request)
    return JsonResponse({'detail': 'Successfully logged out.'})


class SessionView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, format=None):
        return JsonResponse({'isAuthenticated': True})


class WhoAmIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, format=None):
        return JsonResponse({'username': request.user.username})


class PredictorList(APIView):
    """
    List all stock predictors.
    """
    def get(self, request, format=None):
        predictors = StockPredictorModel.objects.all()
        serializer = StockPredictorSerializer(predictors, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        print(f'predictor_list - POST: {data}')
        serializer = StockPredictorSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class PredictorDetail(APIView):
    """
    Retrieve a stock predictor.
    """

    def get_object(self, pk):
        try:
            predictor = StockPredictorModel.objects.get(pk=pk)
        except StockPredictorModel.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        predictor = self.get_object(pk)
        serializer = StockPredictorSerializer(predictor)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        predictor = self.get_object(pk)
        predictor.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class PredictStockVolumeList(APIView):
    """
    List all stock volumes.
    """
    def get(self, request, format=None):
        pred_model = StockPredictorModel.objects.get(name='Predict_Volume_2019_v1_Stock_Model.joblib')
        print('PredictStockVolumeList:', pred_model.name)
        pred_volumes = StockVolumeModel.objects.filter(predict_model=pred_model)
        serializer = StockVolumeSerializer(pred_volumes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        pred_model = StockPredictorModel.objects.get(name='Predict_Volume_2019_v1_Stock_Model.joblib')
        print('StockPredictorModel:', pred_model.name)
        data = JSONParser().parse(request)
        data['predict_model'] = pred_model.id
        pred_volume = get_stock_volume(pred_model, data['price_rolling_med'], data['vol_moving_avg'])
        print('pred_volume:', pred_volume)
        data['predict_volume'] = pred_volume.get('Volume')
        print(f'PredictVolumeList - POST: {data}')
        serializer = StockVolumeSerializer(data=data)
        print(f'PredictVolumeList - serializer: {repr(serializer)}')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class PredictETFVolumeList(APIView):
    """
    List all stock volumes.
    """
    def get(self, request, format=None):
        pred_model = StockPredictorModel.objects.get(name='Predict_Volume_2019_v1_ETF_Model.joblib')
        print('PredictETFVolumeList:', pred_model.name)
        pred_volumes = StockVolumeModel.objects.filter(predict_model=pred_model)
        serializer = StockVolumeSerializer(pred_volumes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        print(f'PredictVolumeList - POST data: {data}')
        pred_model = StockPredictorModel.objects.get(name='Predict_Volume_2019_v1_ETF_Model.joblib')
        data['predict_model'] = pred_model.id
        pred_volume = get_stock_volume(pred_model, data['price_rolling_med'], data['vol_moving_avg'])
        print('pred_volume:', pred_volume)
        data['predict_volume'] = pred_volume.get('Volume')
        serializer = StockVolumeSerializer(data=data)
        print(f'PredictVolumeList - serializer: {repr(serializer)}')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class PredictVolumeDetail(APIView):
    """
    Retrieve or delete a StockVolume
    """

    def get_object(self, pk):
        try:
            pred_volume = StockVolumeModel.objects.get(pk=pk)
        except StockVolumeModel.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        pred_volume = self.get_object(pk)
        serializer = StockVolumeSerializer(pred_volume)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        pred_volume = self.get_object(pk)
        pred_volume.delete()
        return Response(status=HTTP_204_NO_CONTENT)

