import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

from shotglass2.takeabeltof.database import Database, SqliteTable
from instance.site_settings import DATABASE_PATH

db = Database(DATABASE_PATH).connect()
db.execute('PRAGMA foreign_keys = OFF') #Turn off foreign key constraints

db.execute('alter table attendance add column no_show INTEGER DEFAULT 0')

