CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  role ENUM('student','consultant','admin'),
  city VARCHAR(255),
  country VARCHAR(255),
  birthday DATE,
  gender ENUM('male','female','other'),
  access_level ENUM('standard','super') DEFAULT 'standard',
  profile_picture VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (country_name) REFERENCES countries(country_name)
);
