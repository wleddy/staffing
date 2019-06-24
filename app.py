from flask import Flask, g, session, request, redirect, flash, abort, url_for, session
from flask_mail import Mail
from shotglass2 import shotglass
from shotglass2.takeabeltof.database import Database
from shotglass2.takeabeltof.jinja_filters import register_jinja_filters
from shotglass2.takeabeltof.utils import cleanRecordID
from shotglass2.users.views.login import setUserStatus
from shotglass2.users.admin import Admin
from staffing.models import Event, Job, Location, EventType, UserJob

# Create app
# setting static_folder to None allows me to handle loading myself
app = Flask(__name__, instance_relative_config=True,
        static_folder=None,
        )
app.config.from_pyfile('site_settings.py', silent=True)

@app.before_first_request
def start_logging():
    shotglass.start_logging(app)


# work around some web servers that mess up root path
from werkzeug.contrib.fixers import CGIRootFix
if app.config['CGI_ROOT_FIX_APPLY'] == True:
    fixPath = app.config.get("CGI_ROOT_FIX_PATH","/")
    app.wsgi_app = CGIRootFix(app.wsgi_app, app_root=fixPath)

register_jinja_filters(app)


mail = Mail(app)

def init_db(db=None):
    # to support old code
    initalize_all_tables(db)

def initalize_all_tables(db=None):
    """Place code here as needed to initialze all the tables for this site"""
    if not db:
        db = get_db()
        
    shotglass.initalize_user_tables(db)
    
    ### setup any other tables you need here....
    from staffing.models import init_event_db
    init_event_db(db)
    
def get_db(filespec=None):
    """Return a connection to the database.
    If the db path does not exist, create it and initialize the db"""
    
    if not filespec:
        filespec = shotglass.get_site_config()['DATABASE_PATH']
        
    # This is probobly a good place to change the
    # filespec if you want to use a different database
    # for the current request.
    
        
    # test the path, if not found, create it
    initialize = shotglass.make_db_path(filespec)
        
    g.db = Database(filespec).connect()
    if initialize:
        initalize_all_tables(g.db)
            
    return g.db


@app.context_processor
def inject_site_config():
    # Add 'site_config' dict to template context
    c = shotglass.get_site_config()
    return {'site_config':c}
    
    
@app.before_request
def _before():
    # Force all connections to be secure
    if app.config['REQUIRE_SSL'] and not request.is_secure :
        return redirect(request.url.replace("http://", "https://"))

    #ensure that nothing is served from the instance directory
    if 'instance' in request.url:
        return abort(404)
        
    #import pdb;pdb.set_trace()
    session.permanent = True
    
    get_db()
        
    shotglass.set_template_dirs(app)
        
    # Is the user signed in?
    g.user = None
    if 'user_id' in session and 'user' in session:
        # Refresh the user session
        setUserStatus(session['user'],cleanRecordID(session['user_id']))
        
        
    g.admin = Admin(g.db) # This is where user access rules are stored
    
    #Events
    # a header row must have the some permissions or higher than the items it heads
    g.admin.register(Event,url_for('event.display'),display_name='Staffing Admin',header_row=True,minimum_rank_required=500,roles=['admin','event manager'])
    g.admin.register(Event,url_for('event.display'),display_name='Events',minimum_rank_required=500,roles=['admin','event manager'])
    g.admin.register(Job,url_for('signup.roster'),display_name='',minimum_rank_required=80,add_to_menu=False)
    #location
    g.admin.register(Location,url_for('location.display'),display_name='Locations',minimum_rank_required=500,roles=['admin','event manager'])
    g.admin.register(EventType,url_for('event_type.display'),display_name='Event Types',minimum_rank_required=500,roles=['admin','event manager'])

    g.admin.register(UserJob,url_for('attendance.display'),display_name='Attendance',minimum_rank_required=500,roles=['admin','event manager'])

    shotglass.user_setup() # g.admin now holds access rules Users, Prefs and Roles


@app.teardown_request
def _teardown(exception):
    if 'db' in g:
        g.db.close()


#######################
# TODO -- the signup subdomain needs it's own error pages or maybe just it's own layout...
#######################
@app.errorhandler(404)
def page_not_found(error):
    return shotglass.page_not_found(error)

@app.errorhandler(500)
def server_error(error):
    return shotglass.server_error(error)

#Register the static route
# Direct to a specific server for static content
app.add_url_rule('/static/<path:filename>','static',shotglass.static)

from staffing.views import signup, calendar
app.register_blueprint(signup.mod)
app.register_blueprint(calendar.mod)
from staffing.views import event
app.register_blueprint(event.mod)
from staffing.views import location
app.register_blueprint(location.mod)
from staffing.views import job
app.register_blueprint(job.mod)
from staffing.views import event_type
app.register_blueprint(event_type.mod)
from staffing.views import attendance
app.register_blueprint(attendance.mod)

## Setup the routes for users
shotglass.register_users(app)

# setup www.routes...
shotglass.register_www(app)
shotglass.register_maps(app)


@app.route('/')
def default_home():
    # if no subdomain
    return "Know Whan Hom"
    

if __name__ == '__main__':
    
    with app.app_context():
        # create the default database if needed
        initalize_all_tables()
        
    #app.run(host='localhost', port=8000)
    #app.run()
    app.run(host='admin.willie.local')
    
    