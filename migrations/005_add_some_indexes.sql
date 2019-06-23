CREATE INDEX IF NOT EXISTS job_event_start ON job(event_id, start_date);
CREATE INDEX IF NOT EXISTS job_event_location ON job(event_id, location_id);
CREATE INDEX IF NOT EXISTS user_job_job_id ON user_job(job_id);