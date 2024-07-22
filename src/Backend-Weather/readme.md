# Notice

## Configurations:
+ DB	mysql 8.0
+ Server	Python&django

## Dependency:
+ Django==4.2.3 
+ django-cors-headers
+ django-environ==0.10.0 
+ gunicorn==20.0.4

## Note*: You need to change the database configuration in 
1. weatherApp_backend/weatherApp_backend/settings.py 
2. kube-yaml/mysql-deployment.yaml
3. kube-yaml/weatherapp-backend-deployment.yaml
to your own!

## How to use the backend for Cloud on Cloud weather part on your local machine?
1. check the setting.py, change the database setting to your own.
2. run two commands in your terminal:
	a. python manage.py makemigrations
	You may come across several dependency lost here. So you need to download all of them.
	b. python manage.py migrate
With these two commands, python will help you to create the database and the tables!(If a no database error occurs, you will need to create a "weather" db on your own)
3. run the server by entering "python manage.py runserver ${your ip address}:${your port}", now the server is listening for the requests! 
[Note:]If there's any problem with step 3, you may try to enter "python manage.py runserver 0.0.0.0:${your port}", that will make the server listen to all the available
ips. It's unsafe.

## *Deploy mysql service on kubernetes
1. Deploy mysql-pv.yaml
2. Deploy mysql-pvc.yaml
3. Deploy mysql-deployment.yaml
4. Deploy mysql-service.yaml
(Make sure you got the db configurations right in mysql-deployment.yaml!)

## *To deploy the backend on kubernetes with the mysql image
+ Note: make sure you have a mysql service in the cluster and the database configure in settings.py is identical to the database configure in mysql-deployment.yaml. 
1. Deploy the backend deployment yaml and the service yaml.
2. enter the mysql pod ("kubectl exec -it ${pod name} -- /bin/bash", if you are using shell then "kubectl exec -it ${pod name} -- /bin/sh")
3. enter mysql("mysql -u root -p")
4. create a database "weather"(create database weather)
5. exit the pod and enter the backend pod
6. run "python manage.py makemigrations"
7. run "python manage.py migrate"
8. exit the backend pod
9. You have now connect the backend and the database! Try to curl the backend to verify this! (If you want to curl the backend, you need to be inside the cluster.
Or you can choose to forward the port to localhost and test it.)