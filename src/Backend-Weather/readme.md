# Notice

## Configurations:
1. DB: mysql >= 8.0 
2. Python >=
3. Django >= 

## Compile

How to use the backend for Cloud on Cloud weather part?

1. check the setting.py, change the database setting to your own.
2. run two commands in your terminal:
	① python manage.py makemigrations
	② python manage.py migrate
With these two commands, python will help you to create the database and the tables!
3. run the server by entering "python manage.py runserver ${your ip address}:${your port}", now the server is listening for the requests! 
[Note:]If there's any problem with step 3, you may try to enter "python manage.py runserver 0.0.0.0:${your port}", that will make the server listen to all the available
ips. It's unsafe.