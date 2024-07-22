# How to deploy CoC on AWS with k8s

Run the commands under the deployment folder

## Service
+ fsvc.yaml -- LoadBalancer -- expose front-end
  `kubectl apply -f ./1svc/fsvc.yaml`
+ bwsvc.yaml -- NodePort -- expose back-end-weather
  `kubectl apply -f ./1svc/bwsvc.yaml`
+ bcsvc.yaml -- ClusterIP -- expose back-end-chatbox
  `kubectl apply -f ./1svc/bcsvc.yaml`
+ msvc.yaml -- ClusterIP -- expose mysql
  `kubectl apply -f ./1svc/msvc.yaml`

## Database
+ mpv.yaml -- persistent volume
  `kubectl apply -f ./2db/mpv.yaml`
+ mpvc.yaml -- persistent volume claim
  `kubectl apply -f ./2db/mpvc.yaml`
+ mconfig.yaml -- ConfigMap
  `kubectl apply -f ./2db/mconfig.yaml`
+ msecret.yaml -- Secret -- password
  `kubectl apply -f ./2db/msecret.yaml`
+ mysql.yaml -- database
  `kubectl apply -f ./2db/mysql.yaml`
+ exec m-dep pod
  - `kubectl exec -it ${your sql pod name} -- sh`
  - execute `mysql -u root -p`
  - pwd =  `12345678`
  - execute `create database weather;`

## Backend & Database Initialize
+ bwdep.yaml -- deployment -- backend-weather
  - `kubectl apply -f ./3be/bwdep.yaml`
  -  `kubectl autoscale deployment bw-dep --cpu-percent=50 --min=2 --max=5`
  - exec bw-dep pods
    - `kubectl exec -it ${your sql pod name} -- sh`
    - execute `python manage.py makemigrations`
    - execute `python manage.py migrate`
+ bcdep.yaml -- deployment -- backend-chatbox
  - `kubectl apply -f ./3be/bcdep.yaml`
  - `kubectl autoscale deployment bc-dep --cpu-percent=50 --min=1 --max=5`

## Jobs
+ warning_cj.yaml -- job -- provide warning
  - `kubectl apply -f ./4cj/warning_cj.yaml`
+ weather_cj.yaml -- job -- provide weather
  - `kubectl apply -f ./4cj/weather_cj.yaml`
+ predict_cj.yaml -- job -- provide predict
  - `kubectl apply -f ./4cj/predict_cj.yaml`



## Frontend
+ fdep.yaml -- deployment -- front-end
  - `kubectl apply -f ./5fe/fdep.yaml`
  - `kubectl autoscale deployment f-dep --cpu-percent=50 --min=2 --max=10`
