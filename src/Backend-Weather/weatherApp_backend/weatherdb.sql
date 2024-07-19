create database weather;

use weather;

CREATE TABLE weather_info
    ( id INT AUTO_INCREMENT PRIMARY KEY,
      province VARCHAR(50),
      city VARCHAR(50),
      reportTime DATETIME,
      weather VARCHAR(50)
    );

CREATE TABLE temperature_info
    ( id INT AUTO_INCREMENT PRIMARY KEY,
      province VARCHAR(50),
      city VARCHAR(50),
      reportTime DATETIME,
      temperature INT,
      temperature_float FLOAT
    );

CREATE TABLE wind_info
    ( id INT AUTO_INCREMENT PRIMARY KEY,
      province VARCHAR(50),
      city VARCHAR(50),
      reportTime DATETIME,
      winddirection VARCHAR(50),
      windpower VARCHAR(10)
    );

CREATE TABLE humidity_info
    ( id INT AUTO_INCREMENT PRIMARY KEY,
      province VARCHAR(50),
      city VARCHAR(50),
      reportTime DATETIME,
      humidity INT,
      humidity_float FLOAT
    );