CREATE DATABASE IF NOT EXISTS easyabroad;

USE easyabroad;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  surname VARCHAR(50),
  role VARCHAR(20),
  email VARCHAR(100) UNIQUE,
  password TEXT,
  reset_token VARCHAR(64),
  token_expiry DATETIME
);
