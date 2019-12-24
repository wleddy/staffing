.bail on
ALTER TABLE attendance ADD COLUMN input_by NUMBER;
ALTER TABLE attendance ADD COLUMN input_date DATETIME;

UPDATE OR ROLLBACK attendance SET input_by = 'Jeremiah Rohr', input_date = datetime('now') where start_date is not null;
