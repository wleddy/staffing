from flask import g, session, request, redirect, flash, abort, url_for, session, render_template
import os
from shotglass2 import shotglass
from shotglass2.users.models import User, Pref
from shotglass2.takeabeltof.database import Database
from shotglass2.takeabeltof.jinja_filters import register_jinja_filters
from shotglass2.takeabeltof.utils import cleanRecordID
from shotglass2.tools.views import tools
from shotglass2.users.views import user
from shotglass2.users.views.login import setUserStatus
from shotglass2.users.admin import Admin
from staffing.models import Activity, Event, Job, Location, ActivityType, UserJob, EventDateLabel, Client, \
    Attendance, Task, ActivityGroup
from staffing.views import signup, calendar, event, activity,location, job, activity_type, \
    attendance, task, event_date_label, client, activity_group

# Create app
import logging 

app = shotglass.create_app(
        __name__,
        instance_path='../data_store/instance',
        config_filename='site_settings.py',
        static_folder=None,
        )


def start_app():
    shotglass.start_logging(app) # This logs to general purpose log.log 
    initalize_base_tables()
    register_blueprints()
    
    # use os.path.normpath to resolve true path to data file when using '../' shorthand
    shotglass.start_backup_thread(
        os.path.normpath(
            os.path.join(
                app.root_path,shotglass.get_site_config()['DATABASE_PATH']
                )
            )
        )


@app.context_processor
def inject_site_config():
    # Add 'site_config' dict to template context
    return {'site_config':shotglass.get_site_config()}

register_jinja_filters(app)


def get_db(filespec=None):
    """Return a connection to the database.

    If the db path does not exist, create it and initialize the db"""

    if not filespec:
        filespec = shotglass.get_site_config()['DATABASE_PATH']

    # This is probobly a good place to change the
    # filespec if you want to use a different database
    # for the current request.

    # test the path, if not found, try to create it
    if shotglass.make_db_path(filespec):
        g.db = Database(filespec).connect()
        initalize_base_tables(g.db)
    
        return g.db
    else:
        # was unable to create a path to the database
        raise IOError("Unable to create path to () in app.get_db".format(filespec))
    

def init_db(db=None):
    # to support old code
    initalize_base_tables(db)
            
    
@app.before_request
def _before():
    # Force all connections to be secure
    if app.config['REQUIRE_SSL'] and not request.is_secure :
        return redirect(request.url.replace("http://", "https://"))

    #ensure that nothing is served from the instance directory
    if 'instance' in request.url:
        return abort(404)
            
    session.permanent = True
    
    # shotglass.get_site_config(app)
    shotglass.set_template_dirs(app)
    get_db()

    if 'static' in request.url:
        return
    
    # load the saved visit_data into session
    shotglass._before_request(g.db)

        
    # Is the user signed in?
    g.user = None
    is_admin = False
    if 'user_id' in session and 'user' in session:
        # Refresh the user session
        setUserStatus(session['user'],cleanRecordID(session['user_id']))
        is_admin = User(g.db).is_admin(session['user_id'])

    # if site is down and user is not admin, stop them here.
    # will allow an admin user to log in
    down = Pref(g.db).get("Site Down Till",
                        user_name=shotglass.get_site_config().get("HOST_NAME"),
                        default='',
                        description = 'Enter something that looks like a date or time. It will be displayed to visitors and make the site inaccessable. Delete the value to allow access again.',
                        )
    if down and down.value.strip():
        if not is_admin:
            # log the user out...
            from shotglass2.users.views import login
            if g.user:
                login.logout()

            # this will allow an admin to log in.
            if request.url.endswith(url_for('login.login')):
                return login.login()
            
            g.title = "Sorry"
            return render_template('site_down.html',down_till = down.value.strip())
        else:
            flash("The Site is in Maintenance Mode. Changes may be lost...",category='warning')

    create_menus()


def create_menus():
    """Create g.menu_items and g.admin objects.

    g.menu_items is a list of dicts that define the unprotected menu items. 
    They will be displayed to all visitors at the top (or left) of the menus.

    g.admin defines menu items that require a user logged in with at certain level
    of privilege.

    The order in which they are defined is the order in which they are displayed.

    g.menu_items should be a list of dicts
    with keys of 'title' & 'url' used to construct
    the non-table based items in the main menu
    """

    g.menu_items = [
        {'title':'Home','drop_down_menu':[
            {'title':'Events Home','url':url_for('www.home')},
            {'title':'SABA Home','url':'http://sacbike.org'},
            ]
        },
        {'title':'Calendar','url':url_for('calendar.display')},
        {'title':'Signups','url':url_for('signup.display')},
        ]
    
    
    g.admin = Admin(g.db) # This is where user access rules are stored

    #Events
    # a header row must have the some permissions or higher than the items it heads
    #import pdb;pdb.set_trace()
    g.admin.register(Job,url_for('signup.roster'),display_name='View Roster',top_level=True,minimum_rank_required=80,add_to_menu=True)
        
    g.admin.register(Activity,url_for('activity.display'),display_name='Staffing Admin',header_row=True,minimum_rank_required=500,roles=['admin','activity manager'])
    g.admin.register(Activity,url_for('activity.display'),display_name='Activities',minimum_rank_required=500,roles=['admin','activity manager'])
    g.admin.register(Event,url_for('event.display'),display_name='Events',add_to_menu=False,minimum_rank_required=500,roles=['admin','activity manager'])
    #location
    g.admin.register(Location,url_for('location.display'),display_name='Locations',minimum_rank_required=500,roles=['admin','activity manager'])
    g.admin.register(ActivityGroup,url_for('activity_group.display'),display_name='Activity Groups',minimum_rank_required=500,roles=['admin','activity manager'])
    g.admin.register(ActivityType,url_for('activity_type.display'),display_name='Activity Types',minimum_rank_required=500,roles=['admin','activity manager'])
    g.admin.register(EventDateLabel,url_for('event_date_label.display'),display_name='Date Labels',minimum_rank_required=500,roles=['admin','activity manager'])
    g.admin.register(Client,url_for('client.display'),display_name='Clients',minimum_rank_required=500,roles=['admin','activity manager'])
    g.admin.register(Attendance,url_for('attendance.display'),display_name='Attendance',minimum_rank_required=500,roles=['admin','activity manager'])
    g.admin.register(Task,url_for('task.display'),display_name='Ad Hoc Tasks',minimum_rank_required=500,roles=['admin',])
    
    g.admin.register(UserJob,url_for('attendance.display'),display_name='User Jobs',minimum_rank_required=500,roles=['admin','activity manager'],add_to_menu=False)

    # shotglass.user_setup() # g.admin now holds access rules Users, Prefs and Roles
    # This one will set up the view log item
    
    # set up the User menu
    shotglass.set_user_menus()

    #give activity managers access to the user records
    g.admin.register(User,url_for('user.display'),display_name='Users',roles=['activity manager'],add_to_menu=False)

    tools.register_admin() # add the tools menu
    # add this to the tools menu
    g.admin.register(User,
            url_for('signup.volunteer_contact_list'),
            display_name='Download Volunteers',
            minimum_rank_required=500,
        )
        
@app.teardown_request
def _teardown(exception):
    if 'db' in g:
        g.db.close()


@app.errorhandler(404)
def page_not_found(error):
    return shotglass.page_not_found(error)

@app.errorhandler(500)
def server_error(error):
    return shotglass.server_error(error)

def initalize_base_tables(db=None):
    """Place code here as needed to initialze all the tables for this site"""
    if not db:
        db = get_db()
        
    user.initalize_tables(db)
    
    ### setup any other tables you need here....
    from staffing.models import init_event_db
    init_event_db(db)
    

def register_blueprints():
    """Register all your blueprints here and initialize 
    any data tables they need.
    """

    user.register_blueprints(app)
    shotglass.register_www(app)
    app.register_blueprint(tools.mod)

    # # add app specific modules...
    # from starter_module.models import init_db as starter_init
    # starter_init(g.db) #initialize the tables for the module
    # from starter_module.views import starter
    # app.register_blueprint(starter.mod)
    # # update function 'create_menus' to display menu items for the app

    app.register_blueprint(signup.mod)
    app.register_blueprint(activity.mod)
    app.register_blueprint(event.mod)
    app.register_blueprint(job.mod)
    app.register_blueprint(calendar.mod)
    app.register_blueprint(location.mod)
    app.register_blueprint(activity_type.mod)
    app.register_blueprint(attendance.mod)
    app.register_blueprint(task.mod)
    app.register_blueprint(event_date_label.mod)
    app.register_blueprint(client.mod)
    app.register_blueprint(activity_group.mod)
    shotglass.register_maps(app)


#Register the static route
# Direct to a specific server for static content
app.add_url_rule('/static/<path:filename>','static',shotglass.static)

    
app.add_url_rule('/','display',calendar.display) # Make the calendar our home page...


@app.route('/rss', methods=['GET',])
@app.route('/rss/', methods=['GET',])
@app.route('/feed', methods=['GET',])
@app.route('/feed/', methods=['GET',])
def get_rss_feed():
    """Return a fully formed RSS feed of the Event records"""

    from feedme.feedme import FeedMe
    from shotglass2.shotglass import get_site_config
    from shotglass2.takeabeltof.date_utils import local_datetime_now, getDatetimeFromString
    from shotglass2.takeabeltof.jinja_filters import long_date_string, render_markdown
    from staffing.models import Event

    site_config=get_site_config()

    host = request.url_root
    link_root = host.rstrip('/') + url_for('calendar.event')
    
    feeder = FeedMe(title=site_config['SITE_NAME'],
            link = host,
            description = "Future Events from the {} calendar".format(site_config['SITE_NAME']),
            )
        
    recs = Event(g.db).select(
            where="date(event_start_date,'localtime') >= date('{}','localtime')".format(local_datetime_now()),
            order_by = "date(created,'localtime') DESC"
            )
    items = []
    if recs:
        for rec in recs:
            d = {}
            pub_date = getDatetimeFromString(rec.created)
            link = link_root + str(rec.id) + '/'
                
            d.update({'title':rec.event_title})
            d.update({'description':rec.event_description + ' - ' + link})
            d.update({'pubDate':pub_date})
            d.update({'link':link})
            d.update({'permalink':link})
        
            items.append(d)
        
    if not items:
        items.append(
            {'title':'No Upcoming Events',
            'description':'Sorry, there are no upcoming events',
            'pubDate':local_datetime_now(),
            }
        )
    # import pdb;pdb.set_trace()
    feed =  feeder.get_feed(items)
    
    return feed


with app.app_context():
    start_app()
    
    
if __name__ == '__main__':
    #app.run(host='localhost', port=8000)
    #app.run()
    app.run(host='events.willie.local')
    
    