-- Make some users for testing event signups

BEGIN;

INSERT INTO user (first_name,last_name,email,username,active) VALUES ('Doris','Goodman','doris@example.com','doris',1);
INSERT INTO user (first_name,last_name,email,username,active) VALUES ('John','Goodman','John@example.com','John',1);
INSERT INTO user (first_name,last_name,email,username,active) VALUES ('No one','in particular','noone@example.com','none',0);
INSERT INTO user (first_name,last_name,email,username,active) VALUES ('Tim','Valet','tim@example.com','Tim',1);

-- Create some roles for signup
INSERT INTO role (name,rank) VALUES ('activity manager',80);
INSERT INTO role (name,rank) VALUES ('bike valet lead',70);
INSERT INTO role (name,rank) VALUES ('bike mechanic',50);

-- Create user_roles
INSERT INTO user_role (user_id,role_id) VALUES (
    (select id from user where username = 'doris'),
    (select id from role where name = 'activity manager')
);
INSERT INTO user_role (user_id,role_id) VALUES (
    (select id from user where username = 'John'),
    (select id from role where name = 'bike valet lead')
);
INSERT INTO user_role (user_id,role_id) VALUES (
    (select id from user where username = 'Tim'),
    (select id from role where name = 'bike mechanic')
);

COMMIT;
