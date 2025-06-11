-- ─────────────────────────────────────────────────────────────────────────────
-- 02_triggers.sql
-- Contains only the trigger definitions, with a custom DELIMITER to avoid syntax errors.
-- ─────────────────────────────────────────────────────────────────────────────

DELIMITER $$
CREATE TRIGGER trg_after_document_verify
AFTER UPDATE ON uploaded_documents
FOR EACH ROW
BEGIN
  IF OLD.is_valid = FALSE AND NEW.is_valid = TRUE THEN
    DELETE FROM uploaded_documents WHERE id = NEW.id;
  END IF;
END $$
DELIMITER ;