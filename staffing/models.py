from shotglass2.takeabeltof.database import SqliteTable
from shotglass2.takeabeltof.utils import cleanRecordID
from shotglass2.takeabeltof.date_utils import local_datetime_now

        
class Event(SqliteTable):
    """Staffing Event Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'event'
        self.order_by_col = 'lower(title)'
        self.defaults = {}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
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
            location_id INTEGER """
                
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()
        
        
class EventType(SqliteTable):
    """Categorize events"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'event_type'
        self.order_by_col = 'type, id'
        self.defaults = {}

    def create_table(self):
        """Define and create the table"""

        sql = """
        type TEXT NOT NULL,
        description TEXT"""
        
        super().create_table(sql)

    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()


class Job(SqliteTable):
    """Staffing Job Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'job'
        self.order_by_col = 'date(start_date), lower(title)'
        self.defaults = {'max_positions':1,'skill_list':''}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
            title TEXT NULL,
            description TEXT,
            skill_list TEXT,
            start_date DATETIME,
            end_date DATETIME,
            max_positions INTEGER,
            event_id INTEGER,
            location_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES event(id) ON DELETE CASCADE """
                
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()
        
    def filled(self,job_id):
        """Return the number positions filled for this job"""
        out = 0
        cnt = self.db.execute('select sum(positions) as cnt from user_job where job_id=?',(job_id,)).fetchone()[0]
        #import pdb;pdb.set_trace()
        if cnt:
            out = cnt
        return out
        
class UserJob(SqliteTable):
    """Staffing User_Job Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'user_job'
        self.order_by_col = 'id'
        self.defaults = {'positions': 0,}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
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
        FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE """
                
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()
        
    def new(self):
        """Setup a new record"""
        rec = super().new()
        rec.created = local_datetime_now()
        rec.modified = rec.created
        return rec
        
    def save(self,rec,**kwargs):
        rec.modified = local_datetime_now()
        return super().save(rec,**kwargs)
        

class Location(SqliteTable):
    """Staffing Location Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'location'
        self.order_by_col = 'location_name, id'
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
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()


def init_event_db(db):
    """Create a intial user record."""
    Event(db).init_table()
    EventType(db).init_table()
    Job(db).init_table()
    UserJob(db).init_table()
    Location(db).init_table()