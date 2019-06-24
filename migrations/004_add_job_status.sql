.bail on
ALTER TABLE job ADD COLUMN status TEXT;
BEGIN;
-- don't overwrite non null values
UPDATE OR ROLLBACK job SET status = 'Active' where status = null;
COMMIT;