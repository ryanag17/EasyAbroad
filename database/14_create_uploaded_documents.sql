CREATE TABLE IF NOT EXISTS uploaded_documents (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  document_name VARCHAR(255) NOT NULL,
  document_type ENUM('company', 'school') NOT NULL,
  upload_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  verification_date DATETIME,
  is_valid BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX (user_id),
  INDEX (is_valid)
);

DELIMITER $$

CREATE TRIGGER trg_after_document_verify
AFTER UPDATE ON uploaded_documents
FOR EACH ROW
BEGIN
  -- Check if document was just verified
  IF OLD.is_valid = FALSE AND NEW.is_valid = TRUE THEN
    -- Delete the record from table after verification
    DELETE FROM uploaded_documents WHERE id = NEW.id;
    -- Note: This will cause recursion if not handled properly; better handled in backend!
  END IF;
END $$

DELIMITER ;
