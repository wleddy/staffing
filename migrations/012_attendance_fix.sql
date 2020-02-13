-- fix the attendance table with wrong data type

BEGIN;

PRAGMA foreign_keys = OFF;

CREATE TABLE IF NOT EXISTS 'att_temp' (
        id INTEGER NOT NULL PRIMARY KEY,
        user_job_id INTEGER,
        start_date DATETIME,
        end_date DATETIME,
        comment TEXT,
        mileage FLOAT,
        task_user_id INTEGER,
        task_id INTEGER, 
        no_show INTEGER DEFAULT 0, 
        input_by TEXT, 
        input_date DATETIME,
        FOREIGN KEY (task_user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
        FOREIGN KEY (user_job_id) REFERENCES user_job(id) ON DELETE CASCADE
            );

INSERT INTO att_temp SELECT id,user_job_id,start_date,end_date,comment,mileage,task_user_id,task_id,no_show,input_by,input_date  from attendance;
drop table attendance;
alter table att_temp rename to attendance;

PRAGMA foreign_keys = ON;

COMMIT;
