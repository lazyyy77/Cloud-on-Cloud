import pymysql
import pandas as pd

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'xrkacc140810',
    'database': 'weather'
}

def fetch_data_from_db(table_name):
    # 创建数据库连接
    connection = pymysql.connect(**db_config)
    
    # SQL查询语句
    query = "SELECT * FROM " + table_name
    
    # 使用pandas读取SQL查询结果
    df = pd.read_sql(query, connection)
    
    # 关闭数据库连接
    connection.close()
    
    return df

def save_to_excel(df,table_name):
    file_name = table_name + '.xlsx'
    # 将DataFrame保存到Excel文件
    df.to_excel(file_name, index=False)

def save(table_name):
    # 从数据库中获取数据
    df = fetch_data_from_db(table_name)
    
    # 将数据保存到Excel文件
    save_to_excel(df,table_name)

if __name__ == '__main__':
    # save('weather_province_weather_info')
    # save('weather_province_temperature_info')
    # save('weather_province_wind_info')
    # save('weather_province_humidity_info')
    # save('weather_city_weather_info')
    # save('weather_city_temperature_info')
    # save('weather_city_wind_info')
    # save('weather_city_humidity_info')
    save('weather_suggestion')