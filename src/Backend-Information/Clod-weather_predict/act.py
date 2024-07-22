from flask import Flask, jsonify
import pymysql
import json

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'xrkacc140810',
    'database': 'weather'
}

@app.route('/weather', methods=['GET'])
def get_weather():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM weather_info ORDER BY reportTime DESC LIMIT 1")
            weather_info = cursor.fetchone()
            cursor.execute("SELECT * FROM temperature_info ORDER BY reportTime DESC LIMIT 1")
            temperature_info = cursor.fetchone()
            cursor.execute("SELECT * FROM wind_info ORDER BY reportTime DESC LIMIT 1")
            wind_info = cursor.fetchone()
            cursor.execute("SELECT * FROM humidity_info ORDER BY reportTime DESC LIMIT 1")
            humidity_info = cursor.fetchone()

            result = {
                'weather': weather_info,
                'temperature': temperature_info,
                'wind': wind_info,
                'humidity': humidity_info
            }
            return jsonify(result)
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
