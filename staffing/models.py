from shotglass2.takeabeltof.database import SqliteTable
from shotglass2.takeabeltof.utils import cleanRecordID
        
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
            location_id INTEGER """
                
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()
        
        
class Spot(SqliteTable):
    """Staffing Spot Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'spot'
        self.order_by_col = 'date(start_date) DESC, lower(title)'
        self.defaults = {'max_staff':1}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
            title TEXT NULL,
            description TEXT,
            role_list TEXT,
            start_date DATETIME,
            end_date DATETIME,
            max_staff INTEGER,
            event_id INTEGER """
                
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()
        
class UserSpot(SqliteTable):
    """Staffing User_Spot Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'user_spot'
        self.order_by_col = 'id'
        self.defaults = {}
        
    def create_table(self):
        """Define and create the table"""
        
        sql = """
        'user_id' INTEGER NOT NULL,
        'spot_id' INTEGER NOT NULL,
        'attendance_start' DATETIME,
        'attendance_end' DATETIME,
        'attendance_note' TEXT,
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (spot_id) REFERENCES user(id) ON DELETE CASCADE """
                
        super().create_table(sql)
        
    def init_table(self):
        """Create the table and initialize data"""
        self.create_table()

class Location(SqliteTable):
    """Staffing Location Table"""
    def __init__(self,db_connection):
        super().__init__(db_connection)
        self.table_name = 'location'
        self.order_by_col = 'id'
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
    Spot(db).init_table()
    UserSpot(db).init_table()
    Location(db).init_table()