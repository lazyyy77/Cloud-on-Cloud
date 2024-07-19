from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class WeatherInfo(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    reportTime = models.DateTimeField()
    weather = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.province} - {self.city} ({self.reportTime})"


class TemperatureInfo(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    reportTime = models.DateTimeField()
    temperature = models.IntegerField()
    temperature_float = models.FloatField()

    def __str__(self):
        return f"{self.province} - {self.city} ({self.reportTime})"


class WindInfo(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    reportTime = models.DateTimeField()
    winddirection = models.CharField(max_length=50)
    windpower = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.province} - {self.city} ({self.reportTime})"


class HumidityInfo(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    reportTime = models.DateTimeField()
    humidity = models.IntegerField()
    humidity_float = models.FloatField()

    def __str__(self):
        return f"{self.province} - {self.city} ({self.reportTime})"


class ProvinceWeatherInfo(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    reportTime = models.DateTimeField()
    weather = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.province} - {self.city} ({self.reportTime})"


class ProvinceTemperatureInfo(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    reportTime = models.DateTimeField()
    temperature = models.IntegerField()
    temperature_float = models.FloatField()

    def __str__(self):
        return f"{self.province} - {self.city} ({self.reportTime})"


class ProvinceWindInfo(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    reportTime = models.DateTimeField()
    winddirection = models.CharField(max_length=50)
    windpower = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.province} - {self.city} ({self.reportTime})"


class ProvinceHumidityInfo(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    reportTime = models.DateTimeField()
    humidity = models.IntegerField()
    humidity_float = models.FloatField()

    def __str__(self):
        return f"{self.province} - {self.city} ({self.reportTime})"


class WeatherPredictInfo(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    reportTime = models.DateTimeField()
    weather = models.CharField(max_length=50)
    temperature_float = models.FloatField()
    humidity_float = models.FloatField()
    winddirection = models.CharField(max_length=50)
    windpower = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.province} - {self.city} ({self.reportTime})"
# Create your models here.
