CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  role ENUM('student','consultant','admin'),
  city VARCHAR(255),
  country VARCHAR(255),
  created_at DATETIME,
  updated_at DATETIME
);
