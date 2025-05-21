CREATE TABLE IF NOT EXISTS admins (
  user_id INT PRIMARY KEY,
  access_level ENUM('standard','super') DEFAULT 'standard',
  notes TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
