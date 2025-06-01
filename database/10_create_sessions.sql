CREATE TABLE IF NOT EXISTS sessions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  booking_id INT UNIQUE,  -- one session per booking
  video_link VARCHAR(255),
  started_at DATETIME,
  ended_at DATETIME,
  pre_session_notes TEXT,
  post_session_notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (booking_id) REFERENCES bookings(id)
);
