from django.urls import path
from . import views

urlpatterns = [
    # 城市界面路由，获取城市最新的所有信息
    path('get_city_info/', views.get_city_info, name='get_city_info'),
    path('get_city_predict_info/', views.get_city_predict_info, name='get_city_predict_info'),

    # 主页面会使用的路由
    path('get_province_info/', views.get_province_info, name='get_province_info'),
    path('get_all_province_info/', views.get_all_province_info, name='get_all_province_info'),
    path('get_all_weather/', views.get_all_weather, name='get_all_weather'),
    path('get_all_temperature/', views.get_all_temperature, name='get_all_temperature'),
    path('get_all_wind/', views.get_all_wind, name='get_all_wind'),
    path('get_all_humidity/', views.get_all_humidity, name='get_all_humidity'),
]
