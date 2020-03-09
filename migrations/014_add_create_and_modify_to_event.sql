-- Add created and modified fields to event table.

.bail on

ALTER TABLE event ADD COLUMN created DATETIME;
ALTER TABLE event ADD COLUMN modified DATETIME;

-- add a default date
UPDATE event SET created = datetime('2020-03-08 00:00:00'), modified = datetime('2020-03-08 00:00:00');

.bail off
