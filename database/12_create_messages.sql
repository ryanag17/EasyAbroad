-- Messages table
CREATE TABLE IF NOT EXISTS messages (
  id INT PRIMARY KEY AUTO_INCREMENT,
  sender_id INT NOT NULL,
  receiver_id INT NOT NULL,
  booking_id INT,
  encrypted_message VARBINARY(512) NOT NULL,
  encryption_iv VARBINARY(16) NOT NULL,
  is_reported BOOLEAN DEFAULT FALSE,
  reported_at DATETIME,
  sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at DATETIME DEFAULT (CURRENT_TIMESTAMP + INTERVAL 3 YEAR),
  FOREIGN KEY (sender_id) REFERENCES users(id),
  FOREIGN KEY (receiver_id) REFERENCES users(id),
  FOREIGN KEY (booking_id) REFERENCES bookings(id),
  INDEX (booking_id),
  INDEX (sender_id, receiver_id),
  INDEX (sent_at),
  INDEX (expires_at)
);

-- Remove expired messages
DELETE FROM messages
WHERE expires_at < NOW();
