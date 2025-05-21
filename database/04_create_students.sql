CREATE TABLE IF NOT EXISTS students (
  user_id INT PRIMARY KEY,
  birthday DATE,
  gender ENUM('male','female','other'),
  languages TINYTEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
