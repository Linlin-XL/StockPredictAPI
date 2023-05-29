import json
import os

from django.shortcuts import get_object_or_404, get_list_or_404
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

from .models import StockPredictorModel, PredictHistModel
from .serializer import StockPredictorSerializer, PredictHistModelSerializer
from .predict_joblib import predict_model_joblib


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
        items = StockPredictorModel.objects.all()
        serializer = StockPredictorSerializer(items, many=True)
        return Response(serializer.data)


class PredictorDetail(APIView):
    """
    Retrieve a stock predictor.
    """
    def get(self, request, pk, format=None):
        item = get_object_or_404(StockPredictorModel.objects.all(), pk=pk)
        print(f'StockPredictorModel: {item} - {item.__dict__}')
        serializer = StockPredictorSerializer(item)
        return Response(serializer.data)


class StockPredict(APIView):
    """
    Retrieve a stock prediction.
    """
    def post(self, request, stock_type, predict_type, *args, **kwargs):
        pred_model = get_list_or_404(StockPredictorModel.objects.all(),
                                     stock_type=stock_type, predict_type=predict_type)

        data = JSONParser().parse(request)
        data['predict_model'] = pred_model[0].id
        print(f'request data: {stock_type} - {predict_type} - {data}')

        result = get_stock_predict(pred_model[0], data)
        if result.get('Error') is not None:
            return Response(result, status=HTTP_400_BAD_REQUEST)

        data.update(result)
        print(f'updated data: {data}')

        serializer = PredictHistModelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

        return Response(result, status=HTTP_201_CREATED)


def get_stock_predict(pred_model, data):
    if not os.path.exists(pred_model.job_path):
        return {'Error': f'Predict model path does not exist: {pred_model.job_path}'}

    # Make predictions
    volume_avg = int(data.get('vol_moving_avg'))
    price_med = float(data.get('price_rolling_med'))
    if pred_model.predict_type == 'Volume':
        request_data = [
            [volume_avg, price_med]
        ]
    else:
        price_std = float(data.get('price_daily_std'))
        request_data = [
            [volume_avg, price_med, price_std]
        ]

    predict_type = pred_model.predict_type.lower()
    print(f'Request_data: {predict_type} - {request_data}')

    result = predict_model_joblib(pred_model.job_path, request_data)
    if result is None:
        return {'Error': f'Predict model does not work.'}

    return {predict_type: result[0]}
