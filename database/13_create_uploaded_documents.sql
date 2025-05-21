CREATE TABLE IF NOT EXISTS uploaded_documents (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  document_name VARCHAR(255),
  document_type ENUM('company', 'school'),
  upload_date DATETIME,
  verification_date DATETIME,
  is_valid BOOLEAN,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
