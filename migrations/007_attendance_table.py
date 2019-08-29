import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

from shotglass2.takeabeltof.database import Database, SqliteTable
from shotglass2.takeabeltof.date_utils import local_datetime_now, date_to_string
from staffing.models import Job, ActivityType, Activity, UserJob, Attendance, Task
from instance.site_settings import DATABASE_PATH

def drop_tables():
    table_list = ['attendance','task','temp_user_job']
    for table in table_list:
        try:
            db.execute("drop table {}".format(table))
            print("Table {} dropped".format(table))
        except:
            print("Table {} not found".format(table))

db = Database(DATABASE_PATH).connect()
db.execute('PRAGMA foreign_keys = OFF') #Turn off foreign key constraints

drop_tables()

attendance_table = Attendance(db)
attendance_table.create_table()
Task(db).create_table()

# create an attendance record for every UserJob record
user_job_recs = UserJob(db).select()
for job in user_job_recs:
    rec = attendance_table.new()
    rec.user_job_id = job.id
    attendance_table.save(rec)
    
db.commit()

# remove the attendance fields from the user_job table
temp_user_job = UserJob(db)
temp_user_job.table_name = 'temp_user_job'
temp_user_job.create_table()

#transfer the current user_job records into the new table
user_job_recs = UserJob(db).select()

for uj_rec in user_job_recs:
    rec = temp_user_job.new()
    temp_user_job.update(rec,uj_rec._asdict())
    temp_user_job.save(rec)

db.commit()
db.execute('drop table user_job')
db.execute('alter table temp_user_job rename to user_job')

