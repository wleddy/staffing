-- add some new fields
BEGIN;
alter table event add client_website TEXT;
alter table event add staff_info TEXT;
COMMIT;