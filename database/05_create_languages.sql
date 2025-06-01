CREATE TABLE IF NOT EXISTS languages (
  id INT PRIMARY KEY AUTO_INCREMENT,
  language_code VARCHAR(10) UNIQUE, 
  language_name VARCHAR(100)         
);
