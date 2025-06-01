CREATE TABLE IF NOT EXISTS user_languages (
  user_id INT,
  language_id INT,
  PRIMARY KEY (user_id, language_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (language_id) REFERENCES languages(id)
);
