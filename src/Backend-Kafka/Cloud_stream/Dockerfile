# 使用官方Python基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到/app目录
COPY . /app

RUN pip install --upgrade pip
RUN pip install xpinyin
RUN pip install pymysql==1.1.1
RUN pip install cryptography
RUN pip install openpyxl
RUN pip install Werkzeug==2.2.2
EXPOSE 5001

ENV DB_HOST=localhost
ENV DB_PORT=3306
ENV DB_USER=root
ENV DB_PASSWORD=xrkacc140810
ENV DB_NAME=weather
ENV KAFKA_HOST=localhost:9092
ENV KAFKA_SERVICE=weather1


# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 运行Python脚本
# CMD ["python", "get_weather0.py"]
# CMD ["python", "get_weather1.py"]
# CMD ["python", "get_weather2.py"]
# CMD ["python", "get_weather3.py"]
CMD ["python", "stream.py"]