import requests
import pymysql
import schedule
import time
import json
import pandas as pd
from xpinyin import Pinyin
from googletrans import Translator
import translate as tr

p = Pinyin()
t = Translator()
# 配置
API_KEY = '20155b8e21446651cdca54c3d5450beb'
BASE_URL = 'https://restapi.amap.com/v3/weather/weatherInfo?'
# CITIES = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']  # 可以添加更多的城市
DB_CONFIG = {
    'host': 'mysql',
    'user': 'root',
    'password': 'xrkacc140810',
    'database': 'weather'
}

host = 'localhost'
port = 3306
user = 'root'
password = 'xrkacc140810'  # 请替换为你的实际密码
database = 'weather'


# DB_CONFIG = {
#     'host': 'weather.cdxwwz7y02zo.us-east-1.rds.amazonaws.com',
#     'user': 'admin',
#     'password': '123456',
#     'database': 'weather',
#     'port': 3306
# }

# 获取天气数据


def get_weather_data(adcode, retries=10):
    params = {
        'city': adcode,
        'key': API_KEY,
        'extensions': 'base',
    }
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['status'] == '1':
                status = data['status']
                count = data['count']
                info = data['info']
                infocode = data['infocode']
                lives = data['lives'][0]  # 因为lives是一个列表，这里取第一个元素

                # province = lives['province']
                # city = lives['city']

                province = tr.translate_province(lives['province'])
                city = p.get_pinyin(lives['city'], '')
                print(lives)

                adcode = lives['adcode']
                print(lives['weather'])
                weather = tr.translate_weather(lives['weather'])
                temperature = lives['temperature']
                winddirection = tr.translate_wind_direction(lives['winddirection'])
                windpower = lives['windpower']
                humidity = lives['humidity']
                reporttime = lives['reporttime']
                temperature_float = lives['temperature_float']
                humidity_float = lives['humidity_float']

                # 打印提取的结果
                print(f"Status: {status}")
                print(f"Count: {count}")
                print(f"Info: {info}")
                print(f"Infocode: {infocode}")
                print("Lives:")
                print(f"  Province: {province}")
                print(f"  City: {city}")

                print(f"  Adcode: {adcode}")
                print(f"  Weather: {weather}")
                print(f"  Temperature: {temperature}")
                print(f"  Winddirection: {winddirection}")
                print(f"  Windpower: {windpower}")
                print(f"  Humidity: {humidity}")
                print(f"  Reporttime: {reporttime}")
                print(f"  Temperature (float): {temperature_float}")
                print(f"  Humidity (float): {humidity_float}")
                return data

            else:
                print(f"API error: {data['info']}")
                return None
        except requests.exceptions.RequestException as req_err:
            print(f"Attempt {attempt + 1} failed: {req_err}")
            attempt += 1
            time.sleep(2)  # 重试前等待一段时间
    print(f"Failed to fetch data for adcode {adcode} after {retries} attempts.")
    return None


# 将数据存入数据库
def save_to_database(data, mode):
    # connection = pymysql.connect(**DB_CONFIG)
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    lives = data['lives'][0]
    province = tr.translate_province(lives['province'])
    city = p.get_pinyin(lives['city'], '')
    reporttime = lives['reporttime']
    weather = tr.translate_weather(lives['weather'])
    temperature = int(lives['temperature'])
    temperature_float = lives['temperature_float']
    winddirection = tr.translate_wind_direction(lives['winddirection'])
    windpower = int(lives['windpower'].replace("≤3", "3"))
    print(windpower)
    humidity = int(lives['humidity'])
    humidity_float = lives['humidity_float']

    if (temperature < 10):
        wear = "overcoat"
    elif (temperature < 20 and temperature >= 10):
        wear = "ong-sleeve shirt"
    elif (temperature >= 20):
        wear = "T-shirt"
    #
    if (weather == "Clear" or weather == "Cloudy"):
        umbrella = "no"
    else:
        umbrella = "yes"

    if (weather == "Clear" or weather == "Cloudy"):
        car = "yes"
    else:
        car = "no"

    if (temperature < 35 and temperature >= 5 and (
            weather == "Clear" or weather == "Cloudy" or weather == "Overcast" or weather == "Light Rain") and windpower <= 5):
        go_out = 'yes'
    else:
        go_out = 'no'

    print(f"wear: {wear}")
    print(f"umbrella: {umbrella}")
    print(f"car: {car}")
    print(f"go_out: {go_out}")
    if mode == 0:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO weather_provinceweatherinfo (province, city, reportTime, weather) VALUES (%s, %s, %s, %s)",
                    (province, city, reporttime, weather))
                cursor.execute(
                    "INSERT INTO weather_provincetemperatureinfo (province, city, reportTime, temperature, temperature_float) VALUES (%s, %s, %s, %s, %s)",
                    (province, city, reporttime, temperature, temperature_float))
                cursor.execute(
                    "INSERT INTO weather_provincewindinfo (province, city, reportTime, winddirection, windpower) VALUES (%s, %s, %s, %s, %s)",
                    (province, city, reporttime, winddirection, windpower))
                cursor.execute(
                    "INSERT INTO weather_provincehumidityinfo (province, city, reportTime, humidity, humidity_float) VALUES (%s, %s, %s, %s, %s)",
                    (province, city, reporttime, humidity, humidity_float))
            connection.commit()
        finally:
            connection.close()
        print("yes")
    elif mode == 1:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO weather_weatherinfo (province, city, reportTime, weather) VALUES (%s, %s, %s, %s)",
                    (province, city, reporttime, weather))
                cursor.execute(
                    "INSERT INTO weather_temperatureinfo (province, city, reportTime, temperature, temperature_float) VALUES (%s, %s, %s, %s, %s)",
                    (province, city, reporttime, temperature, temperature_float))
                cursor.execute(
                    "INSERT INTO weather_windinfo (province, city, reportTime, winddirection, windpower) VALUES (%s, %s, %s, %s, %s)",
                    (province, city, reporttime, winddirection, windpower))
                cursor.execute(
                    "INSERT INTO weather_humidityinfo (province, city, reportTime, humidity, humidity_float) VALUES (%s, %s, %s, %s, %s)",
                    (province, city, reporttime, humidity, humidity_float))
            connection.commit()
        finally:
            connection.close()
        print("yes")


# # 获取并保存所有城市的天气数据
def fetch_and_store_weather_data(mode=1):
    if mode == 0:
        df = pd.read_excel('各省.xlsx')
    elif mode == 1:
        df = pd.read_excel('几个重点城市.xlsx')
    map_dict = dict(zip(df['中文名'], df['adcode']))
    print(map_dict)
    for city, adcode in map_dict.items():
        weather = get_weather_data(adcode)
        if (weather): save_to_database(weather, mode)


def task():
    # fetch_and_store_weather_data(0)
    fetch_and_store_weather_data(1)


# 定时任务
# schedule.every(1).hour.do(fetch_and_store_weather_data)
schedule.every(1).minutes.do(lambda: task())

if __name__ == '__main__':
    # 初次运行
    fetch_and_store_weather_data(0)
    fetch_and_store_weather_data(1)
    while True:
        schedule.run_pending()
        time.sleep(1)
    # fetch_and_store_weather_data(1)
    # weather= get_weather_data(211381)
    # save_to_database(weather)
    # print(weather)
    # schedule.every(1).hour.do(fetch_and_store_weather_data)

