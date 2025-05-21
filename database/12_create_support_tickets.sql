CREATE TABLE IF NOT EXISTS support_tickets (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  subject VARCHAR(255),
  description TEXT,
  status ENUM('open','in_progress','resolved','closed'),
  created_at DATETIME,
  updated_at DATETIME,
  resolved_by INT,
  resolved_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (resolved_by) REFERENCES admins(user_id)
);
