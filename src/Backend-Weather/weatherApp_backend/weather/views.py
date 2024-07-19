from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import Post, WeatherInfo, TemperatureInfo, WindInfo, HumidityInfo, ProvinceWeatherInfo, \
    ProvinceHumidityInfo, ProvinceTemperatureInfo, ProvinceWindInfo, WeatherPredictInfo
import json
import logging
from django.db.models import F, Max
from django.db.models.functions import datetime

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])  # 只允许GET和OPTIONS请求
def get_city_info(request):
    # 获取单个城市的信息，注意，这里由于只需要一个城市，所以直接将所有天气数据整合之后发给前端
    if request.method == 'GET':
        province = request.GET.get('province', '')
        city = request.GET.get('city', '')

        print(f"Received GET request for province={province}, city={city}")
        if not province or not city:
            return JsonResponse({'error': 'Province and city parameters are required'}, status=400)

        try:
            weather_info = WeatherInfo.objects.filter(province=province, city=city).order_by('-reportTime').first()
            temperature_info = TemperatureInfo.objects.filter(province=province, city=city).order_by(
                '-reportTime').first()
            humidity_info = HumidityInfo.objects.filter(province=province, city=city).order_by('-reportTime').first()
            wind_info = WindInfo.objects.filter(province=province, city=city).order_by('-reportTime').first()

            if not weather_info:
                return JsonResponse({'error': 'Weather info not found'}, status=404)
            if not temperature_info:
                return JsonResponse({'error': 'Temperature info not found'}, status=404)
            if not humidity_info:
                return JsonResponse({'error': 'Humidity info not found'}, status=404)
            if not wind_info:
                return JsonResponse({'error': 'Wind info not found'}, status=404)

            data = {
                'province': weather_info.province,
                'city': weather_info.city,
                'reportTime': weather_info.reportTime.strftime('%Y-%m-%d %H:%M:%S'),
                'weather': weather_info.weather,
                'temperature': temperature_info.temperature,
                'temperature_float': temperature_info.temperature_float,
                'humidity': humidity_info.humidity,
                'humidity_float': humidity_info.humidity_float,
                'wind_direction': wind_info.winddirection,
                'wind_power': int(wind_info.windpower),
            }
            response = JsonResponse({'payload': data})
            response['Access-Control-Allow-Headers'] = '*'
            response['Access-Control-Allow-Origin'] = "*"  # 或者具体允许的来源
            return response

        except WeatherInfo.DoesNotExist:
            return JsonResponse({'error': 'Weather info not found'}, status=404)

    elif request.method == 'OPTIONS':
        response = JsonResponse({
            'message': 'OPTIONS request handled successfully'
        })
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'

        response['Access-Control-Allow-Headers'] = '*'

        response['Access-Control-Allow-Origin'] = '*'

        return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])  # 只允许GET和OPTIONS请求
def get_city_predict_info(request):
    if request.method == 'GET':
        province = request.GET.get('province', '')
        city = request.GET.get('city', '')

        print(f"Received GET predict request for province={province}, city={city}")
        if not province or not city:
            return JsonResponse({'error': 'Province and city parameters are required'}, status=400)

        try:
            predict_info = WeatherPredictInfo.objects.filter(province=province, city=city).order_by('-reportTime').first()

            if not predict_info:
                return JsonResponse({'error': 'Weather info not found'}, status=404)

            data = {
                'province': predict_info.province,
                'city': predict_info.city,
                'reportTime': predict_info.reportTime.strftime('%Y-%m-%d %H:%M:%S'),
                'weather': predict_info.weather,
                'temperature_float': predict_info.temperature_float,
                'humidity_float': predict_info.humidity_float,
                'wind_direction': predict_info.winddirection,
                'wind_power': int(float(predict_info.windpower)),
            }
            response = JsonResponse({'payload': data})
            response['Access-Control-Allow-Headers'] = '*'
            response['Access-Control-Allow-Origin'] = "*"  # 或者具体允许的来源
            return response

        except WeatherInfo.DoesNotExist:
            return JsonResponse({'error': 'Weather info not found'}, status=404)

    elif request.method == 'OPTIONS':
        response = JsonResponse({
            'message': 'OPTIONS request handled successfully'
        })
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'

        response['Access-Control-Allow-Headers'] = '*'

        response['Access-Control-Allow-Origin'] = '*'

        return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])  # 只允许GET和OPTIONS请求
def get_all_weather(request):
    if request.method == "GET":
        print(f"Received GET request for all weather.")
        try:
            # 获取各个城市最近的十条天气数据
            latest_weather = WeatherInfo.objects.annotate(
                report_time_diff=F('reportTime') - datetime.datetime.now()
            ).order_by('-report_time_diff')[:10]

            # 构建返回给前端的数据格式
            weather_data = []
            for weather in latest_weather:
                weather_data.append({
                    'province': weather.province,
                    'city': weather.city,
                    'reportTime': weather.reportTime.strftime('%Y-%m-%d %H:%M:%S'),
                    'weather': weather.weather,
                })

            response = JsonResponse({'payload': weather_data})
            response['Access-Control-Allow-Origin'] = "*"  # 或者具体允许的来源
            return response

        except Exception as e:
            # 处理异常情况
            return JsonResponse({'error': str(e)}, status=500)
    elif request.method == "OPTIONS":
        # 针对OPTIONS请求返回允许的HTTP方法和头部
        print(f"Received OPTIONS request for all weather.")
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"  # 设置允许的来源
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"

        return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])  # 只允许GET和OPTIONS请求
def get_all_temperature(request):
    if request.method == 'GET':

        print(f"Received GET request for all temperature.")

        try:
            temperature_info_list = TemperatureInfo.objects.annotate(
                report_time_diff=F('reportTime') - datetime.datetime.now()
            ).order_by('-report_time_diff')[:10]

            data = []

            for info_item in temperature_info_list:
                data.append({
                    'province': info_item.province,
                    'city': info_item.city,
                    'reportTime': info_item.reportTime.strftime('%Y-%m-%d %H:%M:%S'),
                    'temperature': info_item.temperature,
                    'temperature_float': info_item.temperature_float,
                })

            response = JsonResponse({'payload': data})
            response['Access-Control-Allow-Origin'] = "*"  # 或者具体允许的来源
            return response

        except TemperatureInfo.DoesNotExist:
            return JsonResponse({'error': 'Temperature info not found'}, status=404)
    elif request.method == "OPTIONS":

        print(f"Received OPTIONS request for all temperature.")
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"  # 设置允许的来源
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"

        return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])  # 只允许GET和OPTIONS请求
def get_all_wind(request):
    if request.method == 'GET':

        print(f"Received GET request for all wind.")

        try:
            wind_info_list = WindInfo.objects.annotate(
                report_time_diff=F('reportTime') - datetime.datetime.now()
            ).order_by('-report_time_diff')[:10]

            data = []

            for info_item in wind_info_list:
                data.append({
                    'province': info_item.province,
                    'city': info_item.city,
                    'reportTime': info_item.reportTime.strftime('%Y-%m-%d %H:%M:%S'),
                    'winddirection': info_item.winddirection,
                    'windpower': int(info_item.windpower),
                })

            response = JsonResponse({'payload': data})
            response['Access-Control-Allow-Origin'] = "*"  # 或者具体允许的来源
            return response

        except WindInfo.DoesNotExist:
            return JsonResponse({'error': 'Wind info not found'}, status=404)
    if request.method == 'OPTIONS':
        response = JsonResponse({
            'message': 'OPTIONS request handled successfully'
        })
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'

        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        response['Access-Control-Allow-Origin'] = '*'

        return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])  # 只允许GET和OPTIONS请求
def get_all_humidity(request):
    if request.method == 'GET':

        print(f"Received GET request for all humidity.")

        try:
            humidity_info_list = HumidityInfo.objects.annotate(
                report_time_diff=F('reportTime') - datetime.datetime.now()
            ).order_by('-report_time_diff')[:10]

            data = []

            for info_item in humidity_info_list:
                data.append({
                    'province': info_item.province,
                    'city': info_item.city,
                    'reportTime': info_item.reportTime.strftime('%Y-%m-%d %H:%M:%S'),
                    'humidity': info_item.humidity,
                    'humidity_float': info_item.humidity_float
                })

            response = JsonResponse({'payload': data})
            response['Access-Control-Allow-Origin'] = "*"  # 或者具体允许的来源
            return response

        except HumidityInfo.DoesNotExist:
            return JsonResponse({'error': 'Humidity info not found'}, status=404)
    if request.method == 'OPTIONS':
        response = JsonResponse({
            'message': 'OPTIONS request handled successfully'}
        )
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'

        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        response['Access-Control-Allow-Origin'] = '*'

        return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])  # 只允许GET和OPTIONS请求
def get_province_info(request):
    # 获取单个省份的信息，获取之后整合好发给前端
    if request.method == 'GET':
        province = request.GET.get('province', '')

        print(f"Received GET request for province={province}")
        if not province:
            return JsonResponse({'error': 'The province parameter is required'}, status=400)

        try:
            weather_info = ProvinceWeatherInfo.objects.filter(province=province).last()
            temperature_info = ProvinceTemperatureInfo.objects.filter(province=province).last()
            humidity_info = ProvinceHumidityInfo.objects.filter(province=province).last()
            wind_info = ProvinceWindInfo.objects.filter(province=province).last()
            data = {
                'province': weather_info.province,
                'city': weather_info.city,
                'reportTime': weather_info.reportTime.strftime('%Y-%m-%d %H:%M:%S'),
                'weather': weather_info.weather,
                'temperature': temperature_info.temperature,
                'temperature_float': temperature_info.temperature_float,
                'humidity': humidity_info.humidity,
                'humidity_float': humidity_info.humidity_float,
                'wind_direction': wind_info.winddirection,
                'wind_power': int(wind_info.windpower),
            }
            response = JsonResponse({'payload': data})
            response['Access-Control-Allow-Origin'] = "*"  # 或者具体允许的来源
            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'OPTIONS':
        response = JsonResponse({
            'message': 'OPTIONS request handled successfully'
        })
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'

        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        response['Access-Control-Allow-Origin'] = '*'

        return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])  # 只允许GET和OPTIONS请求
def get_all_province_info(request):
    if request.method == 'GET':
        print(f"Received GET request for all province info")

        try:
            provinces = set()

            # 查询所有省份的最新天气信息
            weather_infos = ProvinceWeatherInfo.objects.values('province').annotate(
                max_reportTime=Max('reportTime')).order_by('-max_reportTime')

            # 查询所有省份的最新温度信息
            temperature_infos = ProvinceTemperatureInfo.objects.values('province').annotate(
                max_reportTime=Max('reportTime')).order_by('-max_reportTime')

            # 查询所有省份的最新湿度信息
            humidity_infos = ProvinceHumidityInfo.objects.values('province').annotate(
                max_reportTime=Max('reportTime')).order_by('-max_reportTime')

            # 查询所有省份的最新风力信息
            wind_infos = ProvinceWindInfo.objects.values('province').annotate(
                max_reportTime=Max('reportTime')).order_by('-max_reportTime')

            # 合并所有省份的信息
            data = []
            for weather_info, temperature_info, humidity_info, wind_info in zip(weather_infos, temperature_infos,
                                                                                humidity_infos, wind_infos):
                province = weather_info['province']
                provinces.add(province)

                # 获取各个信息的最新记录
                weather = ProvinceWeatherInfo.objects.filter(province=province,
                                                             reportTime=weather_info['max_reportTime']).first()
                temperature = ProvinceTemperatureInfo.objects.filter(province=province, reportTime=temperature_info[
                    'max_reportTime']).first()
                humidity = ProvinceHumidityInfo.objects.filter(province=province,
                                                               reportTime=humidity_info['max_reportTime']).first()
                wind = ProvinceWindInfo.objects.filter(province=province,
                                                       reportTime=wind_info['max_reportTime']).first()

                if weather and temperature and humidity and wind:
                    data.append({
                        'province': province,
                        'city': weather.city,
                        'reportTime': weather.reportTime.strftime('%Y-%m-%d %H:%M:%S'),
                        'weather': weather.weather,
                        'temperature': temperature.temperature,
                        'temperature_float': temperature.temperature_float,
                        'humidity': humidity.humidity,
                        'humidity_float': humidity.humidity_float,
                        'wind_direction': wind.winddirection,
                        'wind_power': int(wind.windpower),
                    })

            response = JsonResponse({'payload': data})
            response['Access-Control-Allow-Headers'] = '*'
            response['Access-Control-Allow-Origin'] = "*"  # 或者具体允许的来源
            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'OPTIONS':
        response = JsonResponse({
            'message': 'OPTIONS request handled successfully'
        })
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'

        response['Access-Control-Allow-Headers'] = '*'

        response['Access-Control-Allow-Origin'] = '*'

        return response
# Create your views here.
