CREATE TABLE IF NOT EXISTS 'role' (
            id INTEGER NOT NULL PRIMARY KEY,
            'name' TEXT UNIQUE NOT NULL,
            'description' TEXT,
            'rank' INTEGER DEFAULT 0
            );
CREATE TABLE IF NOT EXISTS 'user_role' (
            id INTEGER NOT NULL PRIMARY KEY,
            'user_id' INTEGER NOT NULL,
            'role_id' INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE
            );
CREATE TABLE IF NOT EXISTS 'user' (
            id INTEGER NOT NULL PRIMARY KEY,
            'first_name' TEXT,
            'last_name' TEXT,
            'email' TEXT UNIQUE COLLATE NOCASE,
            'phone' TEXT,
            'address' TEXT,
            'address2' TEXT,
            'city' TEXT,
            'state' TEXT,
            'zip' TEXT,
            'username' TEXT UNIQUE,
            'password' TEXT,
            'active' INTEGER DEFAULT 1,
            'last_access' DATETIME,
            'access_token' TEXT,
            'access_token_expires' INT,
            'may_send_text' INT,
            'may_send_email' INT
            );
CREATE TABLE IF NOT EXISTS 'pref' (
            id INTEGER NOT NULL PRIMARY KEY,
            name TEXT,
            value TEXT,
            expires DATETIME,
            user_name TEXT
            );
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
CREATE TABLE IF NOT EXISTS 'location' (
            id INTEGER NOT NULL PRIMARY KEY,
        location_name TEXT NOT NULL,
        business_name TEXT,
        street_address TEXT,
        city  TEXT,
        state  TEXT,
        zip TEXT,
        lat  NUMBER,
        lng  NUMBER,
        w3w TEXT
            );
