.bail on
ALTER TABLE event ADD COLUMN prep_status TEXT;
ALTER TABLE event ADD COLUMN event_size TEXT;
ALTER TABLE event ADD COLUMN number_served NUMBER;
ALTER TABLE event ADD COLUMN tips_received NUMBER;
