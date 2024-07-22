import eventlet
eventlet.monkey_patch()

import pymysql
import pandas as pd
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # 导入 Flask-CORS
from kafka import KafkaProducer, KafkaConsumer
import json
import threading
import os

app = Flask(__name__)
CORS(app)  # 启用 CORS
socketio = SocketIO(app, cors_allowed_origins="*")

KAFKA_host=os.getenv('KAFKA_HOST', 'localhost:9092')
KAFKA_service=os.getenv('KAFKA_SERVICE', 'weather1')

producer = KafkaProducer(
    bootstrap_servers=[f'{KAFKA_host}'],  # 使用 Kubernetes 服务名称
    api_version=(2, 1, 2),
    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'xrkacc140810'),
    'database': os.getenv('DB_NAME', 'weather'),
    'port': int(os.getenv('DB_PORT', 3306))
}



def fetch_data_from_db(city_name):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        query = f"SELECT * FROM weather_temperatureinfo WHERE city = '{city_name}' ORDER BY reportTime"
        data = pd.read_sql(query, connection)
        # query = f"SELECT * FROM weather_humidityinfo WHERE city = '{city_name}' ORDER BY reportTime"
        # data_h=pd.read_sql(query, connection)
        # data=pd.merge(data, data_h, on=['province', 'city', 'reportTime'])
    finally:
        connection.close()
    return data

def stream_data(city_name):
    data = fetch_data_from_db(city_name)
    for index, row in data.iterrows():
        row_dict = row.to_dict()
        # 确保所有 Timestamp 对象转换为字符串
        if isinstance(row_dict['reportTime'], pd.Timestamp):
            row_dict['reportTime'] = row_dict['reportTime'].isoformat()
        producer.send(KAFKA_service, row_dict)
        socketio.sleep(1)  # 模拟延迟，调节数据发送速度

@app.route('/start_stream', methods=['POST'])
def start_stream():
    print(request.data)  # 输出收到的请求数据
    print("start stream")
    province = request.json.get('province')
    city = request.json.get('city')
    threading.Thread(target=stream_data, args=(city,)).start()
    return 'Streaming started', 200

def kafka_consumer_task():
    consumer = KafkaConsumer(
        KAFKA_service,
        bootstrap_servers=[f'{KAFKA_host}'],  # 使用 Kubernetes 服务名称
        api_version=(2, 1, 2),
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print('i m here')
    print(consumer)
    while True:
        print('111')
        messages = consumer.poll(timeout_ms=3)
        print(messages)
        for message in consumer:
            data = message.value
            print("Received data from Kafka:", data)
            socketio.emit('weather', data)  # 发送数据到前端的自定义事件，确保前端监听这个事件

if __name__ == '__main__':
    threading.Thread(target=kafka_consumer_task, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5001)
