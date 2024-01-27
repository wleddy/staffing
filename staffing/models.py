from flask import session
from shotglass2.takeabeltof.database import SqliteTable
from shotglass2.takeabeltof.utils import cleanRecordID
from shotglass2.takeabeltof.date_utils import local_datetime_now, date_to_string
from shotglass2.users.models import User, UserRole
        
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
        activity_type_id INTEGER,
        activity_info TEXT,
        contract_date DATETIME,
        total_contract_price NUMBER,
        per_event_contract_price NUMBER,
        contract_notes TEXT
        """
        
        super().create_table(sql)
            

class ActivityGroup(SqliteTable):
    """Logical groups for Activities. At the moment only
    used in the calendar display."""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'activity_group'
        self.order_by_col = 'lower(name), id'
        self.defaults = {}

    def create_table(self):
        """Define and create the table"""

        sql = """
        name TEXT NOT NULL,
        description TEXT,
        display_style TEXT -- a CSS style name
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
        description TEXT,
        activity_group_id INTEGER
        """

        super().create_table(sql)


class Attendance(SqliteTable):
    """Staffing User_Job Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'attendance'
        self.order_by_col = "date(job_start_date,'localtime') DESC , activity_title COLLATE NOCASE ASC, job_title COLLATE NOCASE ASC, first_name COLLATE NOCASE ASC, last_name COLLATE NOCASE ASC"
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
        input_by TEXT, -- the name of person who entered times
        input_date DATETIME,
        FOREIGN KEY (task_user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
        FOREIGN KEY (user_job_id) REFERENCES user_job(id) ON DELETE CASCADE """

        super().create_table(sql)

    def select(self,where=None,order_by=None,**kwargs):
        offset = kwargs.get('offset',0)
        limit = kwargs.get('limit',9999999)
                
        # delay import until needed
        from staffing.views.signup import get_volunteer_role_ids, get_staff_user_ids
                
        # import pdb;pdb.set_trace()
        # get the list of users who have at least one of specified roles
        attn_roles_select = session.get('attn_roles_select')
        user_roles = None
        find_all_users = True # simplify the final query if we can...
        if attn_roles_select and len(attn_roles_select) > 0:
            sql = "select distinct user_id from user_role"
            if 0 not in attn_roles_select:
                # select only by roles
                find_all_users = False
                sql = sql + " where role_id in ({role_ids})".format(role_ids=','.join(str(x) for x in attn_roles_select))
            user_roles = UserRole(self.db).query(sql)
                    
        if not user_roles and attn_roles_select:
            # there are roles selected, but no users have any of those roles - bail now
            return None
            
        staff_only_clause = None
        if user_roles and not find_all_users:
            staff_only_clause = "user_table_id in ({})".format(','.join(str(x.user_id) for x in user_roles))
        if staff_only_clause:
            if not where:
                where = staff_only_clause
            else:
                where = where + " and " + staff_only_clause
            
        if not order_by:
            order_by = self.order_by_col

        sql =  """select
        attendance.*,
        user.id as user_table_id,
        coalesce(job.start_date,attendance.start_date) as job_start_date,
        coalesce(job.end_date,attendance.end_date) as job_end_date,
        coalesce(activity.title,task_activity.title,'No Task Title') as activity_title, 
        coalesce(user.first_name,task_user.first_name) as first_name,
        coalesce(user.last_name,task_user.last_name) as last_name,
        coalesce(user.first_name,task_user.first_name) || 
            ' ' 
            || coalesce(user.last_name,task_user.last_name) as full_name,
        coalesce(nullif(event.calendar_title,''),activity.title,task_activity.title,'No Activity Title') as calendar_title,
        coalesce(job.title,task.name,'No Job Title') as job_title, 
    
        -- 1 if a volunteer job, else 0
        coalesce((select 1 from job_role where job_role.role_id in ({vol_role_ids}) and job_role.job_id = job.id),0) as is_volunteer_job
 
        from attendance
        left join user_job on user_job.id = attendance.user_job_id
        left join job on user_job.job_id = job.id
        left join user on user.id = user_job.user_id
        left join user as task_user on task_user.id = attendance.task_user_id
        left join task on task.id = attendance.task_id
        left join event on event.id = job.event_id
        left join activity as task_activity on task_activity.id = task.activity_id
        left join activity on activity.id = event.activity_id
        left join user_role on user_role.user_id = user.id
    
        where {where}
        group by attendance.id 

        order by {order_by}
        limit {limit}
        offset {offset}
        """.format(
            vol_role_ids=get_volunteer_role_ids(),
            where=where,
            order_by=order_by,
            offset=offset,
            limit=limit,
        )
        
        return self.query(sql)
        
        
    def select_one(self,where=None,order_by=None,**kwargs):
        recs = self.select(where,order_by,**kwargs)
        if recs:
            return recs[0]
            
        return recs
    
        
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
            prep_status TEXT,
            event_size TEXT,
            number_served NUMBER,
            tips_received NUMBER,
            contract_date DATETIME,
            total_contract_price NUMBER,
            per_event_contract_price NUMBER,
            contract_notes TEXT,
            created DATETIME,
            modified DATETIME,
            FOREIGN KEY (activity_id) REFERENCES activity(id) ON DELETE CASCADE
            """
                
        super().create_table(sql)
        
    @property
    def _column_list(self):
            column_list = [
            {'name':'all_day_event','definition':'INTEGER',},
            ]
        
            return column_list
        
    def new(self):
        """Setup a new record"""
        rec = super().new()
        rec.created = local_datetime_now()
        rec.modified = rec.created
        return rec

    def save(self,rec,**kwargs):
        rec.modified = local_datetime_now()
        row_id = super().save(rec,**kwargs)
        return row_id


    def select(self,**kwargs):
        """Extend `select` to include Activity fields in the result set
        """
        
        user_id = kwargs.get('user_id',0)

        sql="""select event.*,
        (select case when '{today}' > event.event_end_date then 1 else 0 end) as is_past_event,
        (select location.location_name from location) as event_default_location_name,
        (select location.street_address from location) as event_default_location_address,
        (select location.city from location) as event_default_location_city,
        (select location.state from location) as event_default_location_state,
        (select location.zip from location) as event_default_location_zip,
        activity_group.display_style as activity_group_style,
        activity_type.activity_group_id,
        -- This is mostly for calendar to know if the user is assigned to this event
        coalesce(
            (select 1 from user_job where {user_id} = user_job.user_id and
             user_job.job_id in (select id from job where job.event_id = event.id  ) LIMIT 1
            ),
        0) as is_yours,
        coalesce(nullif(event.calendar_title,''),activity.title) as event_title,
        activity.title as activity_title,
        coalesce(nullif(event.description,''),activity.description,'') as event_description,
        coalesce(nullif(event.staff_info,''),activity.activity_info,'') as event_staff_info,
        coalesce(nullif(event.contract_date,''),activity.contract_date,'') as event_contract_date,
        activity.contract_date as activity_contract_date,
        coalesce(nullif(event.total_contract_price,''),activity.total_contract_price,'') as event_total_contract_price,
        coalesce(nullif(event.per_event_contract_price,''),activity.per_event_contract_price,'') as event_per_event_contract_price,
        activity.per_event_contract_price as activity_per_event_contract_price,
        coalesce(nullif(event.contract_notes,''),activity.contract_notes,'') as event_contract_notes,
        activity.contract_notes as activity_contract_notes,
        activity.total_contract_price as activity_total_contract_price,
        activity.description as activity_description ,
        (select type from activity_type where activity_type.id = activity.activity_type_id ) as activity_service_type
        from event
        join activity on activity.id = event.activity_id
        left join location on location.id = event.location_id
        left join activity_type on activity_type.id = activity.activity_type_id
        left join activity_group on activity_group.id = activity_type.activity_group_id
        where {where} order by {order_by}
        """.format(
            where=kwargs.get('where',1),
            order_by=kwargs.get('order_by',self.order_by_col),
            user_id=user_id,
            today=date_to_string(local_datetime_now(),'iso_date_tz'),
            )

        return self.query(sql)

    def select_one(self,**kwargs):
        recs = self.select(**kwargs)
        if recs:
            return recs[0]
            
        return recs
        
        
    def get(self, id):
        out = self.select(where=self.table_name + ".id={}".format(cleanRecordID(id)))
        if type(out) == list and len(out) > 0:
            return out[0]
            
        return None


    def locations(self,id):
        """Return a selection of all the locations for the event"""
        loc_ids = set()
        id = cleanRecordID(id)
    
        sql = """select distinct event.location_id as event_loc_id, job.location_id as job_loc_id from event
        left join job on job.event_id = event.id
        where event.id = {}
        """.format(id)

        recs = self.query(sql)
        #import pdb;pdb.set_trace()
        if recs:
            for rec in recs:
                if rec.job_loc_id:
                    # this job has its own location
                    loc_ids.add(rec.job_loc_id)
                elif rec.event_loc_id:
                    # this job is at the default location
                    loc_ids.add(rec.event_loc_id)
            
        if loc_ids:
            return Location(self.db).select(where='id in ({})'.format(','.join(str(x) for x in loc_ids)))
    
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
        if cnt:
            out = cnt
        return out
        
        
    def max_positions(self,job_id):
        """Return the maximum number of positions for this job"""
        out = 0
        cnt = self.db.execute('select max_positions from job where id=?',(job_id,)).fetchone()[0]
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
        activity_id INTEGER,
        FOREIGN KEY (activity_id) REFERENCES activity(id) ON DELETE CASCADE """

        super().create_table(sql)

    def select(self,**kwargs):
        sql ="""select task.*,activity.title as activity_name 
        from task 
        join activity on activity.id = task.activity_id 
        where {where}
        order by {order_by}""".format(
            where=kwargs.get('where',1),
            order_by=kwargs.get('order_by',self.order_by_col),
            )
        
        return self.query(sql)


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
        """Return a list of user records assigned to this job or None"""
        #import pdb;pdb.set_trace()
        user_jobs = self.select(where='job_id = {}'.format(job_id))
        if user_jobs:
            user_ids = [str(user_job.user_id) for user_job in user_jobs]
            users = User(self.db).select(where='user.id in ({})'.format(','.join(user_ids)))
            return users
        else:
            return None


def init_event_db(db):
    """Create tables if needed."""
    Activity(db).create_table()
    ActivityGroup(db).create_table()
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
    