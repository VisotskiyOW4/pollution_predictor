from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/rivers/', views.rivers_json, name='rivers_json'),
    path('api/predictions/', views.predict_for_river, name='predict_for_river'),
    path('api/predict/', views.create_prediction, name='create_prediction'),
]
