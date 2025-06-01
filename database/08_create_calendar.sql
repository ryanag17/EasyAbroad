CREATE TABLE IF NOT EXISTS Calendar (
  user_id INT,
  available_day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
  available_time_start TIME,
  available_time_end TIME,
  PRIMARY KEY (user_id, available_day, available_time_start),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
