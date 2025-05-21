CREATE TABLE IF NOT EXISTS bookings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT,
  consultant_id INT,
  status ENUM('pending','confirmed','cancelled','completed'),
  booked_at DATETIME,
  scheduled_time DATETIME,
  duration_minutes INT,
  FOREIGN KEY (student_id) REFERENCES students(user_id),
  FOREIGN KEY (consultant_id) REFERENCES consultants(user_id)
);
