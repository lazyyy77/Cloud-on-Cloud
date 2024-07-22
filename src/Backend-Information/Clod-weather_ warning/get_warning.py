import requests
import pymysql
import schedule
import time
import json
import map
import os
import pandas as pd
from datetime import datetime
import pytz
import translate as tr
from xpinyin import Pinyin

p = Pinyin()
# 配置
API_KEY = '9eea7e731f3e486894981cdf08e9e79b'
BASE_URL = 'https://devapi.qweather.com/v7/warning/now?'
# CITIES = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']  # 可以添加更多的城市
host = os.getenv('DB_HOST', 'localhost')
port = int(os.getenv('DB_PORT', 3306))
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', 'xrkacc140810') # 请替换为你的实际密码
database =  os.getenv('DB_NAME', 'weather')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'xrkacc140810'),
    'database': os.getenv('DB_NAME', 'weather'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# 获取天气数据


def get_weather_data(locationID, retries=10):
    params = {
        'key': API_KEY,
        'location':locationID,
        'lang':'zh'

    }
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            print(data)
            return data

        except requests.exceptions.RequestException as req_err:
            print(f"Attempt {attempt + 1} failed: {req_err}")
            attempt += 1
            time.sleep(2)  # 重试前等待一段时间
    print(f"Failed to fetch data for  {locationID} after {retries} attempts.")
    return None


# 将数据存入数据库
def save_to_database(province,city,data):
    province=tr.translate_province(province)
    city = p.get_pinyin(city, '')
    connection = pymysql.connect(**DB_CONFIG)

    updateTime1=data['updateTime']
    dt = datetime.fromisoformat(updateTime1)

    # 转换为UTC时间
    dt_utc = dt.astimezone(pytz.UTC)

    # 格式化为SQL需要的时间格式
    updateTime = dt_utc.strftime('%Y-%m-%d %H:%M:%S')
    hourly=data['warning']
    try:
        for record in hourly:
                startTime = record['startTime']
                endTime = record['endTime']
                dt = datetime.fromisoformat(startTime)
                # 转换为UTC时间
                dt_utc = dt.astimezone(pytz.UTC)
                # 格式化为SQL需要的时间格式
                startTime = dt_utc.strftime('%Y-%m-%d %H:%M:%S')

                dt = datetime.fromisoformat(endTime)
                # 转换为UTC时间
                dt_utc = dt.astimezone(pytz.UTC)
                endTime = dt_utc.strftime('%Y-%m-%d %H:%M:%S')

                title=record['title']
                status=record['status']
                level=record['level']
                severity=record['severity']
                severityColor=record['severityColor']
                typeName=record['typeName']
                text=record['text']

                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO weather_warninginfo (province, city, reportTime, startTime ,endTime,title,status,level,severity,severityColor,typeName,text) VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s,%s)",
                                         (province, city, updateTime, startTime,endTime,title,status,level,severity,severityColor,typeName,text))
                connection.commit()
    finally:
        connection.close()

    # try:
    #     with connection.cursor() as cursor:
    #         # cursor.execute("INSERT INTO weather_info (province, city, reportTime, weather) VALUES (%s, %s, %s, %s)",
    #         #                (province, city, reporttime, weather))
    #         # cursor.execute(
    #         #     "INSERT INTO temperature_info (province, city, reportTime, temperature, temperature_float) VALUES (%s, %s, %s, %s, %s)",
    #         #     (province, city, reporttime, temperature, temperature_float))
    #         # cursor.execute(
    #         #     "INSERT INTO wind_info (province, city, reportTime, winddirection, windpower) VALUES (%s, %s, %s, %s, %s)",
    #         #     (province, city, reporttime, winddirection, windpower))
    #         # cursor.execute(
    #         #     "INSERT INTO humidity_info (province, city, reportTime, humidity, humidity_float) VALUES (%s, %s, %s, %s, %s)",
    #         #     (province, city, reporttime, humidity, humidity_float))
    #     connection.commit()
    # finally:
    #     connection.close()r
    print("yes")


# # 获取并保存所有城市的天气数据
def fetch_and_store_weather_data():
    df = pd.read_excel('citylist.xlsx')
    map_dict = dict(zip(zip(df['province_name'], df['city_name'],), df['Location_ID']))
    print(map_dict)
    for name, Location_ID, in map_dict.items():
         weather = get_weather_data(Location_ID)
         if (weather): save_to_database(name[0],name[1],weather)


# 定时任务
# schedule.every(1).hour.do(fetch_and_store_weather_data)

if __name__ == '__main__':
    # 初次运行
    # fetch_and_store_weather_data()
    #  weather= get_weather_data(101010300,10)
     # save_to_database('北京','朝阳',weather)
    # print(weather)
     fetch_and_store_weather_data();

