from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.users.models import Role
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString
from staffing.models import Activity, Location, Task, UserTask
from staffing.utils import pack_list_to_string, un_pack_string

mod = Blueprint('signup',__name__, template_folder='templates/signup', url_prefix='/signup')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.signup')
    g.title = 'Signup'


@mod.route('/')
def display():
    """List Signup opportuniies"""
    setExits()
    
    listing = []
    activities = Activity(g.db).select() #will need to filter by date and access
    #import pdb;pdb.set_trace()
    for activity in activities:
        listing.append({'activity':activity})
        location = Location(g.db).get(activity.location_id)
        listing[-1]['location'] = location
        # tasks will also need to filter by date and access
        tasks = Task(g.db).select(where = "activity_id = {}".format(activity.id))
        listing[-1]['tasks'] = tasks
    
    return render_template('signup_list.html',listing=listing)
        

@mod.route('/signup/<int:task_id>/',methods=['GET','POST',])
@mod.route('/signup/<int:task_id>',methods=['GET','POST',])
@mod.route('/signup',methods=['GET','POST',])
def signup(task_id=0):
    """Add or remove a signup
    May come from a modal dialog"""
    setExits()
    return "{} Task ID {}".format(g.title,task_id)
    
    