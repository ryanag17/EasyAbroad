CREATE TABLE IF NOT EXISTS consultant_reviews (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  booking_id      INT NOT NULL UNIQUE,
  student_id      INT NOT NULL,
  consultant_id   INT NOT NULL,
  rating          TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  review_text     TEXT,
  submitted_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
  FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (consultant_id) REFERENCES users(id) ON DELETE CASCADE
);
