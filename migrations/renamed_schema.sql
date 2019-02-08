-- Rename some tables and copy data.
-- Use the create, copy, drop to be backward compatible in sqlite3

PRAGMA foreign_keys = OFF;

begin;

CREATE TABLE IF NOT EXISTS "event" (
            id INTEGER NOT NULL PRIMARY KEY,
            title TEXT NULL,
            description TEXT,
            image_url TEXT,
            manager_name TEXT,
            manager_email TEXT,
            manager_phone TEXT,
            client_contact TEXT,
            client_email TEXT,
            client_phone TEXT,
            event_type_id INTEGER,
            location_id INTEGER
            );
CREATE TABLE IF NOT EXISTS "event_type" (
        id INTEGER NOT NULL PRIMARY KEY,
        type TEXT NOT NULL,
        description TEXT
            );
CREATE TABLE IF NOT EXISTS "job" (
            id INTEGER NOT NULL PRIMARY KEY,
            title TEXT NULL,
            description TEXT,
            skill_list TEXT,
            start_date DATETIME,
            end_date DATETIME,
            max_positions INTEGER,
            event_id INTEGER,
            location_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES "event"(id) ON DELETE CASCADE
            );
CREATE TABLE IF NOT EXISTS "user_job" (
        id INTEGER NOT NULL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        created DATETIME,
        modified DATETIME,
        positions INTEGER,
        attendance_start DATETIME,
        attendance_end DATETIME,
        attendance_comment TEXT,
        attendance_mileage FLOAT,
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (job_id) REFERENCES "job"(id) ON DELETE CASCADE
            );

insert into event select * from event;
insert into event_type select * from event_type;
insert into job select * from job;
insert into user_job select * from user_job;
    
drop table event;
drop table event_type;
drop table job;
drop table user_job;

commit;
