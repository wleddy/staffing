-- Add some fields to the Activitiy and Event tables
-- to hold information about the contracts


.bail on

ALTER TABLE activity ADD COLUMN contract_date DATETIME;
ALTER TABLE activity ADD COLUMN total_contract_price NUMBER;
ALTER TABLE activity ADD COLUMN per_event_contract_price NUMBER;
ALTER TABLE activity ADD COLUMN contract_notes TEXT;

-- fix an issue that has not been discovered yet. Table was not defined properly
ALTER TABLE activity ADD COLUMN activity_info TEXT;


ALTER TABLE event ADD COLUMN contract_date DATETIME;
ALTER TABLE event ADD COLUMN total_contract_price NUMBER;
ALTER TABLE event ADD COLUMN per_event_contract_price NUMBER;
ALTER TABLE event ADD COLUMN contract_notes TEXT;

.bail off
