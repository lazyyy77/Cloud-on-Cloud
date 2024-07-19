# Generated by Django 5.0.7 on 2024-07-10 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0002_rename_report_time_weatherinfo_reporttime'),
    ]

    operations = [
        migrations.CreateModel(
            name='HumidityInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('province', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('reportTime', models.DateTimeField()),
                ('humidity', models.IntegerField()),
                ('humidity_float', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='TemperatureInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('province', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('reportTime', models.DateTimeField()),
                ('temperature', models.IntegerField()),
                ('temperature_float', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='WindInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('province', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('reportTime', models.DateTimeField()),
                ('winddirection', models.CharField(max_length=50)),
                ('windpower', models.CharField(max_length=10)),
            ],
        ),
    ]