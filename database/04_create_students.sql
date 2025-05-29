CREATE TABLE IF NOT EXISTS students (
  user_id INT PRIMARY KEY,
  birthday DATE,
  gender ENUM('male','female','other'),
  languages TINYTEXT,
  profile_picture VARCHAR(255)
  FOREIGN KEY (user_id) REFERENCES users(id)
);
