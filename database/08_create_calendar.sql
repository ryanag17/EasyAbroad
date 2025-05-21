CREATE TABLE IF NOT EXISTS Calendar (
  user_id INT PRIMARY KEY,
  available_day VARCHAR(255),
  available_time_start TIME,
  available_time_end TIME,
  FOREIGN KEY (user_id) REFERENCES consultants(user_id)
);
