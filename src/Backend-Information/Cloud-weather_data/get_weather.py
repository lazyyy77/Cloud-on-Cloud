import requests
import pymysql
import schedule
import time
import os
import json
import pandas as pd
from xpinyin import Pinyin
from googletrans import Translator
import translate as tr
from concurrent.futures import ThreadPoolExecutor, as_completed

p = Pinyin()
t = Translator()

API_KEY = '20155b8e21446651cdca54c3d5450beb'
BASE_URL = 'https://restapi.amap.com/v3/weather/weatherInfo?'

host = os.getenv('DB_HOST', 'localhost')
port = int(os.getenv('DB_PORT', 3306))
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', 'xrkacc140810')
database = os.getenv('DB_NAME', 'weather')

DB_CONFIG = {
    'host': host,
    'user': user,
    'password': password,
    'database': database,
    'port': port
}

def get_weather_data(adcode):
    params = {
        'city': adcode,
        'key': API_KEY,
        'extensions': 'base',
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=100)
        response.raise_for_status()
        data = response.json()
        if data['status'] == '1':
            lives = data['lives'][0]
            province = tr.translate_province(lives['province'])
            city = p.get_pinyin(lives['city'], '')
            weather = tr.translate_weather(lives['weather'])
            temperature = int(lives['temperature'])
            temperature_float = lives['temperature_float']
            winddirection = tr.translate_wind_direction(lives['winddirection'])
            windpower = int(lives['windpower'].replace("≤3", "3"))
            humidity = int(lives['humidity'])
            humidity_float = lives['humidity_float']
            reporttime = lives['reporttime']

            wear = "T-shirt" if temperature >= 20 else "long-sleeve shirt" if temperature >= 10 else "overcoat"
            umbrella = "no" if weather in ["Clear", "Cloudy"] else "yes"
            car = "yes" if weather in ["Clear", "Cloudy"] else "no"
            go_out = 'yes' if (temperature < 32 and temperature >= 5 and weather in ["Clear", "Cloudy", "Overcast", "Light Rain"] and windpower <= 5) else 'no'

            return (province, city, reporttime, weather, temperature, temperature_float, winddirection, windpower, humidity, humidity_float, wear, umbrella, car, go_out)
        else:
            print(f"API error: {data['info']}")
            return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request failed: {req_err}")
        return None

def save_to_database(weather_data, mode):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            if mode == 0:
                cursor.executemany(
                    "INSERT INTO weather_provinceweatherinfo (province, city, reportTime, weather) VALUES (%s, %s, %s, %s)",
                    [(wd[0], wd[1], wd[2], wd[3]) for wd in weather_data])
                cursor.executemany(
                    "INSERT INTO weather_provincetemperatureinfo (province, city, reportTime, temperature, temperature_float) VALUES (%s, %s, %s, %s, %s)",
                    [(wd[0], wd[1], wd[2], wd[4], wd[5]) for wd in weather_data])
                cursor.executemany(
                    "INSERT INTO weather_provincewindinfo (province, city, reportTime, winddirection, windpower) VALUES (%s, %s, %s, %s, %s)",
                    [(wd[0], wd[1], wd[2], wd[6], wd[7]) for wd in weather_data])
                cursor.executemany(
                    "INSERT INTO weather_provincehumidityinfo (province, city, reportTime, humidity, humidity_float) VALUES (%s, %s, %s, %s, %s)",
                    [(wd[0], wd[1], wd[2], wd[8], wd[9]) for wd in weather_data])
            elif mode == 1:
                cursor.executemany(
                    "INSERT INTO weather_weatherinfo (province, city, reportTime, weather) VALUES (%s, %s, %s, %s)",
                    [(wd[0], wd[1], wd[2], wd[3]) for wd in weather_data])
                cursor.executemany(
                    "INSERT INTO weather_temperatureinfo (province, city, reportTime, temperature, temperature_float) VALUES (%s, %s, %s, %s, %s)",
                    [(wd[0], wd[1], wd[2], wd[4], wd[5]) for wd in weather_data])
                cursor.executemany(
                    "INSERT INTO weather_windinfo (province, city, reportTime, winddirection, windpower) VALUES (%s, %s, %s, %s, %s)",
                    [(wd[0], wd[1], wd[2], wd[6], wd[7]) for wd in weather_data])
                cursor.executemany(
                    "INSERT INTO weather_humidityinfo (province, city, reportTime, humidity, humidity_float) VALUES (%s, %s, %s, %s, %s)",
                    [(wd[0], wd[1], wd[2], wd[8], wd[9]) for wd in weather_data])
                cursor.executemany(
                    "INSERT INTO weather_suggestion (province, city, reportTime, wear, umbrella, car, go_out) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    [(wd[0], wd[1], wd[2], wd[10], wd[11], wd[12], wd[13]) for wd in weather_data])
            connection.commit()
    except Exception as exc:
        print(f" insert generated an exception: {exc}")
    finally:
        connection.close()

def fetch_and_store_weather_data(mode=1):
    if mode == 0:
        df = pd.read_excel('各省.xlsx')
    elif mode == 1:
        df = pd.read_excel('city数据all.xlsx')
    map_dict = dict(zip(df['中文名'], df['adcode']))

    weather_data_list = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_city = {executor.submit(get_weather_data, adcode): city for city, adcode in map_dict.items()}
        for future in as_completed(future_to_city):
            city = future_to_city[future]
            try:
                data = future.result()
                if data:
                    weather_data_list.append(data)
            except Exception as exc:
                print(f"{city} generated an exception: {exc}")

    if weather_data_list:
        save_to_database(weather_data_list, mode)

def task():
    fetch_and_store_weather_data(0)
    fetch_and_store_weather_data(1)

if __name__ == '__main__':
    fetch_and_store_weather_data(0)
    fetch_and_store_weather_data(1)
