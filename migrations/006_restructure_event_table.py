import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

from shotglass2.takeabeltof.database import Database, SqliteTable
from shotglass2.takeabeltof.date_utils import local_datetime_now, date_to_string
from staffing.models import Event, Client, EventDateLabel, Job, EventType, Activity, UserJob
from instance.site_settings import DATABASE_PATH

def drop_tables():
    table_list = ['activity','temp_event','activity','client','temp_job','event_date_label','temp_user_job']
    for table in table_list:
        try:
            db.execute("drop table {}".format(table))
            print("Table {} dropped".format(table))
        except:
            print("Table {} not found".format(table))
            
db = Database(DATABASE_PATH).connect()
db.execute('PRAGMA foreign_keys = OFF') #Turn off foreign key constraints

drop_tables()


EventDateLabel(db).create_table()
event_labels = ['Bike Valet Open','Bike Valet Close','Event Start','Event Close',]
eventlabel = EventDateLabel(db)
for label in event_labels:
    rec = eventlabel.get(label)
    if not rec:
        rec = eventlabel.new()
        rec.label = label
        eventlabel.save(rec)
        
db.commit()

client = Client(db)
client.create_table()
temp_event = Event(db)
temp_event.table_name = "temp_event"
temp_event.create_table()
activity_table = Activity(db)
activity_table.create_table()

job_table = Job(db)
new_job_table = Job(db)

new_job_table.table_name = "temp_job"
new_job_table.create_table()

assignment_table = UserJob(db)
new_assignment_table = UserJob(db)
new_assignment_table.table_name = "temp_user_job"
new_assignment_table.create_table()

#import pdb; pdb.set_trace()
old_event_table = Event(db)
old_events = old_event_table.select()
if old_events:
    for old_event_rec in old_events:
        #import pdb; pdb.set_trace()
        activity_rec = activity_table.new()
        activity_rec.title = old_event_rec.title
        activity_rec.description = old_event_rec.description
        activity_table.save(activity_rec)
        old_event_rec.description = None
        
        job_dates = job_table.query(" select substr(start_date,1,10) as job_date from job where event_id = {} group by job_date".format(old_event_rec.id))
        if job_dates:
            for job_date in job_dates:
                # create a new event record for this date
                new_event_rec = temp_event.new()
                temp_event.update(new_event_rec,old_event_rec._asdict())
                new_event_rec.activity_id = activity_rec.id
                temp_event.save(new_event_rec)
                
                #process all the jobs for this event/date
                jobs = job_table.select(where="event_id= {} and substr(start_date,1,10) == '{}'".format(old_event_rec.id,job_date.job_date))
                # Get the Start and end dates for this event based on related Jobs
                event_start_date = None
                event_end_date = None
                service_start_date = None #date_to_string(local_datetime_now(),'iso_date_tz')
                service_end_date = None
                for job in jobs:
                    if job.status == "Public Calendar":
                        service_start_date = event_start_date = job.start_date 
                        service_end_date = event_end_date = job.end_date 

                    if job.status == "Active":
                        new_job_rec = new_job_table.new()
                        new_job_table.update(new_job_rec,job._asdict())
                        new_job_rec.event_id = new_event_rec.id
                        new_job_table.save(new_job_rec)
                        
                        # Create new assignments for this job
                        #import pdb; pdb.set_trace()
                        
                        old_assignments = assignment_table.select(where="job_id = {}".format(job.id))
                        if old_assignments:
                            for assmnt in old_assignments:
                                new_assmt = new_assignment_table.new()
                                new_assignment_table.update(new_assmt,assmnt._asdict())
                                new_assmt.job_id = new_job_rec.id
                                new_assignment_table.save(new_assmt)
                                
            
            
            
                # set the start and end dates for the event
                new_event_rec.event_start_date = event_start_date if event_start_date else service_start_date
                new_event_rec.event_end_date = event_end_date if event_end_date else service_end_date
                new_event_rec.service_start_date = service_start_date if service_start_date else event_start_date
                new_event_rec.service_end_date = service_end_date if service_end_date else event_end_date
                # Set the time labels based on the event type
                # these ids are hard wired per the new table definition
                new_event_rec.event_end_date_label_id = 3 
                new_event_rec.event_start_date_label_id = 4
                new_event_rec.service_end_date_label_id = 1 if new_event_rec.event_type_id <=2 else 3
                new_event_rec.service_start_date_label_id = 2  if new_event_rec.event_type_id <=2 else 4
            
                # Create or find client record
                if old_event_rec.client_contact:
                    client_rec = client.select_one(where="name = '{}'".format(old_event_rec.client_contact))
                    if not client_rec:
                        client_rec = client.new()
                        client_rec.name = old_event_rec.client_contact
                        client_rec.website = old_event_rec.client_website
                        client_rec.email = old_event_rec.client_email
                        client_rec.phone = old_event_rec.client_phone
                        # Most of the old contact names are people, so split it into first and last
                        contact_name = old_event_rec.client_contact.split(' ')
                        for pos in range(2):
                            if len(contact_name) > pos:
                                if pos == 0:
                                    client_rec.contact_first_name = contact_name[pos]
                                else:
                                    client_rec.contact_last_name = contact_name[pos]
                                    
                        client.save(client_rec)
                        # clear these fields in new event record
                        new_event_rec.client_contact = None
                        new_event_rec.client_phone = None
                        new_event_rec.client_email = None
                        new_event_rec.client_website = None
                
                    new_event_rec.client_id = client_rec.id
        
                temp_event.save(new_event_rec)
                print(activity_rec.title)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print("Changes rolled back. Error = {}".format(str(e)))
            break
        
db.close()
