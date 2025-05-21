CREATE TABLE IF NOT EXISTS sessions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  booking_id INT,
  video_link VARCHAR(255),
  started_at DATETIME,
  ended_at DATETIME,
  notes TEXT,
  FOREIGN KEY (booking_id) REFERENCES bookings(id)
);
