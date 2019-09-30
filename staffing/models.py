from shotglass2.takeabeltof.database import SqliteTable
from shotglass2.takeabeltof.utils import cleanRecordID
from shotglass2.takeabeltof.date_utils import local_datetime_now
from shotglass2.users.models import User
        
class Activity(SqliteTable):
    """Events are grouped under Activiies
    """
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'activity'
        self.order_by_col = 'lower(title), id'
        self.defaults = {}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
        title TEXT,
        description TEXT,
        activity_type_id INTEGER
        activity_info TEXT
        """
                
        super().create_table(sql)


class ActivityType(SqliteTable):
    """Categorize events"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'activity_type'
        self.order_by_col = 'lower(type), id'
        self.defaults = {}

    def create_table(self):
        """Define and create the table"""

        sql = """
        type TEXT NOT NULL,
        description TEXT
        """

        super().create_table(sql)


class Attendance(SqliteTable):
    """Staffing User_Job Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'attendance'
        self.order_by_col = 'start_date DESC, id'
        self.defaults = {'no_show':0,}
        self.indexes = {"attendance_user_job_id":"user_job_id","attendance_start_date":"start_date"}

    def create_table(self):
        """Define and create the table"""

        sql = """
        user_job_id INTEGER,
        start_date DATETIME,
        end_date DATETIME,
        comment TEXT,
        mileage FLOAT,
        task_user_id INTEGER,
        task_id INTEGER,
        no_show INTEGER DEFAULT 0,
        FOREIGN KEY (task_user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
        FOREIGN KEY (user_job_id) REFERENCES user_job(id) ON DELETE CASCADE """

        super().create_table(sql)


class Client(SqliteTable):
    """Client for events"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'client'
        self.order_by_col = 'lower(name), id'
        self.defaults = {}

    def create_table(self):
        """Define and create the table"""

        sql = """
        name TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        website TEXT,
        email TEXT,
        phone TEXT,
        contact_first_name TEXT,
        contact_last_name TEXT,
        """
        
        super().create_table(sql)


class Event(SqliteTable):
    """Staffing Event Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'event'
        self.order_by_col = 'id'
        self.defaults = {'status':'Scheduled','exclude_from_calendar':0,}
        self.indexes = {"event_activity_id":"activity_id"}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
            activity_id INTEGER,
            description TEXT,
            staff_info TEXT,
            manager_user_id INTEGER,
            client_id INTEGER,
            client_contact TEXT,
            client_email TEXT,
            client_phone TEXT,
            client_website TEXT,
            location_id INTEGER,
            event_start_date DATETIME,
            event_end_date DATETIME,
            event_start_date_label_id INTEGER,
            event_end_date_label_id INTEGER,
            service_start_date DATETIME,
            service_end_date DATETIME,
            service_start_date_label_id INTEGER,
            service_end_date_label_id INTEGER,
            service_type TEXT,
            calendar_title TEXT,
            exclude_from_calendar INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Scheduled',
            FOREIGN KEY (activity_id) REFERENCES activity(id) ON DELETE CASCADE
            """
                
        super().create_table(sql)
        
        
    def select(self,**kwargs):
        """Extend `select` to include Activity fields in the result set
        """
        
        
        sql="""select event.*, activity.title as activity_title, 
        activity.description as activity_description ,
        coalesce(nullif(event.calendar_title,''),activity.title) as event_title,
        (select type from activity_type where activity_type.id = activity.activity_type_id ) as activity_service_type
        from event 
        join activity on activity.id = event.activity_id
        where {} order by {}""".format(kwargs.get('where',1),kwargs.get('order_by',self.order_by_col))
        
        return self.query(sql)
        
    def get(self, id):
        out = self.select(where=self.table_name + ".id={}".format(cleanRecordID(id)))
        if type(out) == list and len(out) > 0:
            return out[0]
            
        return None
        
class EventDateLabel(SqliteTable):
    """A place to put the labels used to make event.<event|service>_start_date and end dates user friendly
    """
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'event_date_label'
        self.order_by_col = 'lower(label), id'
        self.defaults = {}

    def create_table(self):
        """Define and create the table"""

        sql = """
        label TEXT NOT NULL UNIQUE
        """
        
        super().create_table(sql)

    def get(self,label_or_id):
        """select the label record by label or id"""
        if type(label_or_id) is str:
            rec = self.select_one(where='lower(label) = "{}"'.format(label_or_id.lower()))
        else:
            rec = super().get(cleanRecordID(label_or_id))
    
        return rec



class Job(SqliteTable):
    """Staffing Job Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'job'
        self.order_by_col = 'start_date, lower(title)'
        self.defaults = {'max_positions':1,}
        self.indexes = {"job_event_start":"event_id, start_date","job_event_location":"event_id, location_id",}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
            title TEXT NULL,
            description TEXT,
            start_date DATETIME,
            end_date DATETIME,
            max_positions INTEGER,
            event_id INTEGER,
            location_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES event(id) ON DELETE CASCADE
            """
                
        super().create_table(sql)
                
                
    def filled(self,job_id):
        """Return the number positions filled for this job"""
        out = 0
        cnt = self.db.execute('select sum(positions) as cnt from user_job where job_id=?',(job_id,)).fetchone()[0]
        #import pdb;pdb.set_trace()
        if cnt:
            out = cnt
        return out
        
        
class JobRole(SqliteTable):
    """User roles that are required to signup for a job"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'job_role'
        self.order_by_col = 'id'
        self.defaults = {}
        self.indexes = {"job_role_job_id":"job_id","job_role_roll_and_job":"role_id,job_id"}

    def create_table(self):
        """Define and create the table"""

        sql = """
        job_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE,
        FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE """
    
        super().create_table(sql)
        

class Location(SqliteTable):
    """Staffing Location Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'location'
        self.order_by_col = 'lower(location_name), id'
        self.defaults = {}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
        location_name TEXT NOT NULL,
        business_name TEXT,
        street_address TEXT,
        city  TEXT,
        state  TEXT,
        zip TEXT,
        lat  NUMBER,
        lng  NUMBER,
        w3w TEXT """
                
        super().create_table(sql)
        
class StaffNotification(SqliteTable):
    """Staffing Notification Table
    Record that a particular notification has been sent so we don't send it twice.
    """
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'staff_notification'
        self.order_by_col = 'id'
        self.defaults = {}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
        trigger_function_name TEXT,
        event_id INTEGER,
        job_id INTEGER,
        user_id  INTEGER,
        job_start_date  DATETIME,
        run_date DATETIME
        """
                
        super().create_table(sql)
        
        
class Task(SqliteTable):
    """Contains records of ad hoc user activities"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'task'
        self.order_by_col = 'name, id'
        self.defaults = {}
        self.indexes = {}

    def create_table(self):
        """Tasks are Adhock jobs that need to be accounted for but don't appear on the calendar"""

        sql = """
        name TEXT,
        activity_id,
        FOREIGN KEY (activity_id) REFERENCES activity(id) ON DELETE CASCADE """

        super().create_table(sql)


class UserJob(SqliteTable):
    """Staffing User_Job Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'user_job'
        self.order_by_col = 'id'
        self.defaults = {'positions': 0,}
        self.indexes = {"user_job_job_id":"job_id","user_job_user_id":"user_id",}

    def create_table(self):
        """Define and create the table"""

        sql = """
        user_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        created DATETIME,
        modified DATETIME,
        positions INTEGER,
        comment TEXT,
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE """
        
        super().create_table(sql)

    def new(self):
        """Setup a new record"""
        rec = super().new()
        rec.created = local_datetime_now()
        rec.modified = rec.created
        return rec

    def save(self,rec,**kwargs):
        rec.modified = local_datetime_now()
        #import pdb;pdb.set_trace()
        make_attendance_rec = False
        if rec.id == None:
            #a new Attendance record to go with this new user_job record
            make_attendance_rec = True
            
        row_id = super().save(rec,**kwargs)
        
        if make_attendance_rec and row_id != None:
            att = Attendance(self.db)
            att_rec = att.new()
            att_rec.user_job_id = row_id
            att.save(att_rec)
            
        return row_id

    def get_assigned_users(self,job_id):
        """Return a namedlist of user records assigned to this job or None"""
        #import pdb;pdb.set_trace()
        user_jobs = self.select(where='job_id = {}'.format(job_id))
        if user_jobs:
            user_ids = [str(user_job.user_id) for user_job in user_jobs]
            users = User(self.db).select(where='id in ({})'.format(','.join(user_ids)))
            return users
        else:
            return None


def init_event_db(db):
    """Create a intial user record."""
    Activity(db).create_table()
    ActivityType(db).create_table()
    Attendance(db).create_table()
    Client(db).create_table()
    Event(db).create_table()
    EventDateLabel(db).create_table()
    Job(db).create_table()
    JobRole(db).create_table()
    Location(db).create_table()
    StaffNotification(db).create_table()
    Task(db).create_table()
    UserJob(db).create_table()
    