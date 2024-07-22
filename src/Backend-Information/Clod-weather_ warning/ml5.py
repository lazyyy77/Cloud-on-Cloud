import pandas as pd
import numpy as np
import pymysql
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import torch
import torch.nn as nn
import torch.optim as optim
import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os
os.system('chcp 65001') # explicitly changed encoding to utf-8

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'xrkacc140810',
    'database': 'weather'
}

spark = SparkSession.builder \
    .appName("WeatherPrediction") \
    .getOrCreate()


# def fetch_data_from_db(city_name):
#     connection = pymysql.connect(**DB_CONFIG)
#
#     temp_query = f"SELECT * FROM weather_city_temperature_info WHERE city = '{city_name}'"
#     humidity_query = f"SELECT * FROM weather_city_humidity_info WHERE city = '{city_name}'"
#     wind_query = f"SELECT * FROM weather_city_wind_info WHERE city = '{city_name}'"
#
#     temp_data = pd.read_sql(temp_query, connection)
#     humidity_data = pd.read_sql(humidity_query, connection)
#     wind_data = pd.read_sql(wind_query, connection)
#
#     connection.close()
#
#     data = pd.merge(temp_data, humidity_data, on=['province', 'city', 'reportTime'])
#     data = pd.merge(data, wind_data, on=['province', 'city', 'reportTime'])
#     return data

def fetch_data_from_db(city_name):
    connection = pymysql.connect(**DB_CONFIG)

    query = f"SELECT * FROM weather_city_temperature_info WHERE city = '{city_name}'"
    temp_data = spark.read.jdbc(url=f"jdbc:mysql://{DB_CONFIG['host']}/{DB_CONFIG['database']}",
                                table=f"({query}) as temp", properties=DB_CONFIG)

    query = f"SELECT * FROM weather_city_humidity_info WHERE city = '{city_name}'"
    humidity_data = spark.read.jdbc(url=f"jdbc:mysql://{DB_CONFIG['host']}/{DB_CONFIG['database']}",
                                    table=f"({query}) as humidity", properties=DB_CONFIG)

    query = f"SELECT * FROM weather_city_wind_info WHERE city = '{city_name}'"
    wind_data = spark.read.jdbc(url=f"jdbc:mysql://{DB_CONFIG['host']}/{DB_CONFIG['database']}",
                                table=f"({query}) as wind", properties=DB_CONFIG)

    connection.close()

    data = temp_data.join(humidity_data, ['province', 'city', 'reportTime']) \
        .join(wind_data, ['province', 'city', 'reportTime'])
    data.show()
    data = data.toPandas()
    print(data)
    return data


def preprocess_data(city_name):
    data = fetch_data_from_db(city_name)

    scaler_temp = StandardScaler()
    scaler_humidity = StandardScaler()
    scaler_windpower = StandardScaler()

    data['temperature_normalized'] = scaler_temp.fit_transform(data['temperature_float'].values.reshape(-1, 1))
    data['humidity_normalized'] = scaler_humidity.fit_transform(data['humidity_float'].values.reshape(-1, 1))
    data['windpower_normalized'] = scaler_windpower.fit_transform(data['windpower'].values.reshape(-1, 1))

    seq_length = 10
    features = data[['temperature_normalized', 'humidity_normalized', 'windpower_normalized']].values
    target_temp = data['temperature_normalized'].values
    target_humidity = data['humidity_normalized'].values
    target_windpower = data['windpower_normalized'].values

    X, y_temp = create_sequences(features, seq_length)
    _, y_humidity = create_sequences(target_humidity, seq_length)
    _, y_windpower = create_sequences(target_windpower, seq_length)

    return X, y_temp, y_humidity, y_windpower, scaler_temp, scaler_humidity, scaler_windpower


def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:i + seq_length]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, num_layers):
        super(LSTMModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc_temp = nn.Linear(hidden_dim, output_dim[0])
        self.fc_humidity = nn.Linear(hidden_dim, output_dim[1])
        self.fc_windpower = nn.Linear(hidden_dim, output_dim[2])

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = out[:, -1, :]
        temp_out = self.fc_temp(out)
        humidity_out = self.fc_humidity(out)
        windpower_out = self.fc_windpower(out)
        return temp_out, humidity_out, windpower_out


def train_model(city_name, province):
    X, y_temp, y_humidity, y_windpower, scaler_temp, scaler_humidity, scaler_windpower = preprocess_data(city_name)

    X_train, X_test, y_temp_train, y_temp_test, y_humidity_train, y_humidity_test, y_windpower_train, y_windpower_test = train_test_split(
        X, y_temp, y_humidity, y_windpower, test_size=0.2, random_state=42)

    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    y_temp_train_tensor = torch.tensor(y_temp_train, dtype=torch.float32)
    y_humidity_train_tensor = torch.tensor(y_humidity_train, dtype=torch.float32)
    y_windpower_train_tensor = torch.tensor(y_windpower_train, dtype=torch.float32)
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
    y_temp_test_tensor = torch.tensor(y_temp_test, dtype=torch.float32)
    y_humidity_test_tensor = torch.tensor(y_humidity_test, dtype=torch.float32)
    y_windpower_test_tensor = torch.tensor(y_windpower_test, dtype=torch.float32)

    input_dim = X_train.shape[2]
    hidden_dim = 64
    output_dim = [1, 1, 1]
    num_layers = 2
    num_epochs = 50

    model = LSTMModel(input_dim, hidden_dim, output_dim, num_layers)
    criterion_temp = nn.MSELoss()
    criterion_humidity = nn.MSELoss()
    criterion_windpower = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(num_epochs):
        model.train()
        optimizer.zero_grad()
        outputs_temp, outputs_humidity, outputs_windpower = model(X_train_tensor)
        loss_temp = criterion_temp(outputs_temp, y_temp_train_tensor.unsqueeze(1))
        loss_humidity = criterion_humidity(outputs_humidity, y_humidity_train_tensor.unsqueeze(1))
        loss_windpower = criterion_windpower(outputs_windpower, y_windpower_train_tensor.unsqueeze(1))
        loss = loss_temp + loss_humidity + loss_windpower
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

    torch.save(model.state_dict(), 'lstm_model.pth')
    joblib.dump(scaler_temp, 'scaler_temp.pkl')
    joblib.dump(scaler_humidity, 'scaler_humidity.pkl')
    joblib.dump(scaler_windpower, 'scaler_windpower.pkl')
    return model


def predict_weather(city_name, province):
    X, y_temp, y_humidity, y_windpower, scaler_temp, scaler_humidity, scaler_windpower = preprocess_data(city_name)

    X_tensor = torch.tensor(X, dtype=torch.float32)

    input_dim = X.shape[2]
    hidden_dim = 64
    output_dim = [1, 1, 1]
    num_layers = 2

    model = LSTMModel(input_dim, hidden_dim, output_dim, num_layers)
    model.load_state_dict(torch.load('lstm_model.pth'))
    model.eval()

    with torch.no_grad():
        predicted_temp, predicted_humidity, predicted_windpower = model(X_tensor)

    predicted_temperature = scaler_temp.inverse_transform(predicted_temp.numpy().reshape(-1, 1))
    predicted_humidity = scaler_humidity.inverse_transform(predicted_humidity.numpy().reshape(-1, 1))
    predicted_windpower = scaler_windpower.inverse_transform(predicted_windpower.numpy().reshape(-1, 1))

    connection = pymysql.connect(**DB_CONFIG)
    weather_query = f"SELECT distinct weather, reportTime FROM weather_city_weather_info WHERE city = '{city_name}' ORDER BY reportTime DESC LIMIT 1"
    wind_query = f"SELECT distinct winddirection, reportTime FROM weather_city_wind_info WHERE city = '{city_name}' ORDER BY reportTime DESC LIMIT 1"

    weather_data = pd.read_sql(weather_query, connection)
    wind_data = pd.read_sql(wind_query, connection)

    connection.close()

    predict_weather = weather_data['weather'][0]
    predict_winddirection = wind_data['winddirection'][0]

    print(f"未来1小时{city_name}的天气预测: {predict_weather}")
    print(f"未来1小时{city_name}的温度预测: {predicted_temperature[-1][0]:.2f}°C")
    print(f"未来1小时{city_name}的湿度预测: {predicted_humidity[-1][0]:.2f}%")
    print(f"未来1小时{city_name}的风力预测: {predicted_windpower[-1][0]:.2f}")
    print(f"未来1小时{city_name}的风向预测: {predict_winddirection}")

    data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO weather_weatherpredictinfo (province, city, reportTime, weather, temperature_float, humidity_float, windpower, winddirection) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (province, city_name, data_time, predict_weather, predicted_temperature[-1][0],
                 predicted_humidity[-1][0], predicted_windpower[-1][0], predict_winddirection))
        connection.commit()
    finally:
        connection.close()


def update_predict():
    df = pd.read_excel('重点城市英文名.xlsx')
    print(df['区县名'])
    map_dict = dict(zip(df['区县名'], df['省份']))
    for city, province in map_dict.items():
        # train_model(city, province)
        predict_weather(city, province)


update_predict()
