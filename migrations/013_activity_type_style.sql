-- adds the option to add a CSS style to each Activity type
.bail on

alter table activity_type add column activity_group_id INTEGER;


.bail off
