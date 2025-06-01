CREATE TABLE IF NOT EXISTS bookings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT,
  consultant_id INT,
  status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
  booked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  scheduled_start DATETIME,
  scheduled_end DATETIME,
  reason ENUM('accommodation', 'social_life', 'uni_info', 'travel_info', 'company_info'),
  platform ENUM('zoom', 'microsoft_teams', 'google_meet', 'apple_facetime'),
  FOREIGN KEY (student_id) REFERENCES users(id),
  FOREIGN KEY (consultant_id) REFERENCES users(id)
);

UPDATE bookings 
SET status = 'completed' 
WHERE status = 'confirmed' AND scheduled_end < NOW();
