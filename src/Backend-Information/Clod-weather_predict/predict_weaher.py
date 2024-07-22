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
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def fetch_data_from_db(province,city_name):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        temp_query = f"SELECT * FROM weather_temperatureinfo WHERE city = '{city_name}' and province ='{province}'"
        humidity_query = f"SELECT * FROM weather_humidityinfo WHERE city = '{city_name}' and province ='{province}'"
        wind_query = f"SELECT * FROM weather_windinfo WHERE city = '{city_name}' and province ='{province}'"

        temp_data = pd.read_sql(temp_query, connection)
        humidity_data = pd.read_sql(humidity_query, connection)
        wind_data = pd.read_sql(wind_query, connection)

        data = pd.merge(temp_data, humidity_data, on=['province', 'city', 'reportTime'])
        data = pd.merge(data, wind_data, on=['province', 'city', 'reportTime'])
    finally:
        connection.close()
    return data

def preprocess_data(province,city_name):
    print(province,city_name)
    data = fetch_data_from_db(province,city_name)

    scaler_temp = StandardScaler()
    scaler_humidity = StandardScaler()
    scaler_windpower = StandardScaler()

    data['temperature_normalized'] = scaler_temp.fit_transform(data[['temperature_float']])
    data['humidity_normalized'] = scaler_humidity.fit_transform(data[['humidity_float']])
    data['windpower_normalized'] = scaler_windpower.fit_transform(data[['windpower']])

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
    model_file = f'{province}_lstm_model.pth'
    if os.path.exists(model_file):
        print(f'Model for {province} already exists. Loading the model and scalers...')
        return

    X, y_temp, y_humidity, y_windpower, scaler_temp, scaler_humidity, scaler_windpower = preprocess_data(province,city_name)

    # if len(X) < 2:
    #     print(f"Sample size too small for {city_name}. Skipping training.")
    #     return

    X_train, X_test, y_temp_train, y_temp_test, y_humidity_train, y_humidity_test, y_windpower_train, y_windpower_test = train_test_split(
        X, y_temp, y_humidity, y_windpower, test_size=0.2, random_state=42)

    if len(X_train) == 0 or len(X_test) == 0:
        print(f"Sample size too small after train/test split for {city_name}. Using the latest data for prediction.")
        return

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

    torch.save(model.state_dict(), model_file)


def predict_weather(city_name, province):
    # scaler_temp = joblib.load('scaler_temp.pkl')
    # scaler_humidity = joblib.load('scaler_humidity.pkl')
    # scaler_windpower = joblib.load('scaler_windpower.pkl')

    seq_length = 10
    X, y_temp, y_humidity, y_windpower, scaler_temp, scaler_humidity, scaler_windpower = preprocess_data(province,city_name)
    if len(X) == 0:
        print(f"Sample size too small for {city_name}. Unable to predict. 6")
        print(X)
        return

    X_tensor = torch.tensor(X, dtype=torch.float32)

    input_dim = X.shape[2]
    hidden_dim = 64
    output_dim = [1, 1, 1]
    num_layers = 2
    if os.path.exists(f'{province}_lstm_model.pth'):
        train_model(city_name, province)
    if os.path.exists(f'{province}_lstm_model.pth'):
        model = LSTMModel(input_dim, hidden_dim, output_dim, num_layers)
        model.load_state_dict(torch.load(f'{province}_lstm_model.pth'))
        model.eval()

        with torch.no_grad():
            predicted_temp, predicted_humidity, predicted_windpower = model(X_tensor)

        predicted_temperature = scaler_temp.inverse_transform(predicted_temp.numpy().reshape(-1, 1))
        predicted_humidity = scaler_humidity.inverse_transform(predicted_humidity.numpy().reshape(-1, 1))
        predicted_windpower = scaler_windpower.inverse_transform(predicted_windpower.numpy().reshape(-1, 1))

        connection = pymysql.connect(**DB_CONFIG)
        try:
            weather_query = f"SELECT distinct weather, reportTime FROM weather_weatherinfo WHERE city = '{city_name}' ORDER BY reportTime DESC LIMIT 1"
            wind_query = f"SELECT distinct winddirection, reportTime FROM weather_windinfo WHERE city = '{city_name}' ORDER BY reportTime DESC LIMIT 1"

            weather_data = pd.read_sql(weather_query, connection)
            predict_weather = weather_data['weather'][0]
            wind_data = pd.read_sql(wind_query, connection)
            predict_winddirection = wind_data['winddirection'][0]
            predicted_temperature1=predicted_temperature[-1][0]
            predicted_humidity1= predicted_humidity[-1][0]
            predicted_windpower1=predicted_windpower[-1][0]
        finally:
            connection.close()
    else:
        connection = pymysql.connect(**DB_CONFIG)
        try:
            weather_query = f"SELECT distinct weather, reportTime FROM weather_weatherinfo WHERE city = '{city_name}' and province='{province}' ORDER BY reportTime DESC LIMIT 1"
            wind_query = f"SELECT distinct winddirection,windpower, reportTime FROM weather_windinfo WHERE city = '{city_name}' and province='{province}' ORDER BY reportTime DESC LIMIT 1"
            temperature_query=f"SELECT distinct temperature, reportTime FROM weather_temperatureinfo WHERE city = '{city_name}' and province='{province}' ORDER BY reportTime DESC LIMIT 1"
            humidity_query=f"SELECT distinct humidity, reportTime FROM weather_humidityinfo WHERE city = '{city_name}' and province='{province}' ORDER BY reportTime DESC LIMIT 1"
            weather_data = pd.read_sql(weather_query, connection)
            predict_weather = weather_data['weather'][0]
            wind_data = pd.read_sql(wind_query, connection)
            predict_winddirection = wind_data['winddirection'][0]
            predicted_windpower1=wind_data['windpower'][0]
            temperature_data=pd.read_sql(temperature_query, connection)
            predicted_temperature1=temperature_data['temperature'][0]
            humidity_data=pd.read_sql(humidity_query, connection)
            predicted_humidity1=humidity_data['humidity'][0]
        finally:
            connection.close()

    data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO weather_weatherpredictinfo (province, city, reportTime, weather, temperature_float, humidity_float, windpower, winddirection) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [(province, city_name, data_time, predict_weather, predicted_temperature1, predicted_humidity1, predicted_windpower1, predict_winddirection)])
        connection.commit()
    finally:
        connection.close()

    print(f"未来1小时{city_name}的天气预测: {predict_weather}")
    print(f"未来1小时{city_name}的温度预测: {predicted_temperature1:.2f}°C")
    print(f"未来1小时{city_name}的湿度预测: {predicted_humidity1:.2f}%")
    print(f"未来1小时{city_name}的风力预测: {predicted_windpower1:.2f}")
    print(f"未来1小时{city_name}的风向预测: {predict_winddirection}")

def update_predict():
    df = pd.read_excel('重点城市英文名.xlsx')
    map_dict = dict(zip(df['区县名'], df['省份']))
    print(map_dict)

    with ThreadPoolExecutor(max_workers=5) as executor:
    #     futures = [executor.submit(train_model, city, province) for city, province in map_dict.items()]
    #     for future in as_completed(futures):
    #         future.result()

        futures = [executor.submit(predict_weather, city, province) for city, province in map_dict.items()]
        for future in as_completed(futures):
            future.result()

if __name__ == '__main__':
    update_predict()
