-- Add created and modified fields to event table.

.bail on

ALTER TABLE event ADD COLUMN created DATETIME;
ALTER TABLE event ADD COLUMN modified DATETIME;

-- add a default date
UPDATE event SET created = datetime('now'), modified = datetime('now');

.bail off
