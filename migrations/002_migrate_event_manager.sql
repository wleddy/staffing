-- Link Event to a manager in User table
-- there is no data to migrate at this time

.bail on

begin;

CREATE TABLE IF NOT EXISTS "event_temp" (
            id INTEGER NOT NULL PRIMARY KEY,
            title TEXT NULL,
            description TEXT,
            manager_user_id INTEGER,
            client_contact TEXT,
            client_email TEXT,
            client_phone TEXT,
            event_type_id INTEGER,
            location_id INTEGER
            );

INSERT INTO event_temp SELECT id, title, description, NULL, client_contact, client_email, client_phone, event_type_id, location_id from event;
drop table event;
alter table event_temp rename to event;

commit;

.bail off


