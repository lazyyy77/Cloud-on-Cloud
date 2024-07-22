Cloud-weather_data:获取天气数据

Cloud-weather_predict：预测天气

Cloud—weather_info:获取天气预警

Cloud_weather_stream:获取历史天气变化后端

部署到K8S的方法：获取，预测预警部分，打开对应文件夹下的cornjob.yaml文件即可（e.g：weather-cornjob.yaml)
将其中```yaml```文件中的```env```环境变量改成需要连接的数据库即可。然后
```
kubectl apply -f weather-cornjob.yaml
```
集群上部署kafka：
打开```kafka-29.3.8/kafka```：
```
helm install -n kafka kafka .
```
value.yaml已配置好，直接部署即可

Cloud_weather_stream后端部署：
修改```flask.yaml```中的```env```环境变量，```KAFKA_HOST```，```KAFKA_TOPIC```为刚刚部署上去的kafka的ip地址和topic
```
kubectl apply -f flask.yaml
```

也可以通过自己生成镜像来从头部署，dockerfile在每个文件夹中都已写好
