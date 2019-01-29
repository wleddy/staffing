from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.shotglass import get_app_config
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString, local_datetime_now
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.users.models import Role, User
from staffing.models import Activity, Location, Task, UserTask
from staffing.utils import pack_list_to_string, un_pack_string


mod = Blueprint('signup',__name__, template_folder='templates/signup', url_prefix='/signup')


def setExits():
    g.listURL = url_for('.display')
    g.title = 'Signup'


@mod.route('/')
def display():
    """List Signup opportuniies"""
    setExits()
    
    listing = []
    sql = """
    select activity.id as activity_id, activity.title as activity_title, activity.description as activity_description,
    act_location.id as act_loc_id,
    act_location.location_name as act_loc_name,
    act_location.lat as act_loc_lat,
    act_location.lng as act_loc_lng,
    (select datetime(task.start_date) from task where task.activity_id = activity.id 
        order by datetime(task.start_date) limit 1 ) as active_first_date, 
    (select coalesce(sum(user_task.positions),0) from user_task 
        where task.id = user_task.task_id) as activity_filled_positions,
    (select coalesce(sum(task.max_positions),1) from task 
        where task.activity_id = activity.id) as activity_max_positions,
    (select distinct coalesce(count(task.id),1) from task 
        where task.activity_id = activity.id and task.location_id not null and 
        task.location_id <> activity.location_id) as unique_task_locations,
    task.id as task_id,
    task.title as task_title,
    task.description as task_description,
    task.start_date,
    task.end_date,
    task.max_positions,
    task.skill_list,
    task_location.id as task_loc_id,
    task_location.location_name as task_loc_name,
    task_location.lat as task_loc_lat,
    task_location.lng as task_loc_lng,

    null as participants, -- just a place holder
    (select coalesce(sum(user_task.positions),0) from user_task 
        where task.id = user_task.task_id and task.activity_id = activity.id) as task_filled_positions
    from task
    join activity on activity.id = task.activity_id
    left join location as act_location on act_location.id = activity.location_id
    left join location as task_location on task_location.id = task.location_id
    where date(task.start_date) >= date('{}')
    order by active_first_date, task.start_date
    """.format(local_datetime_now().isoformat()[:10],)
    
    #import pdb;pdb.set_trace()
    # get the current users role id's
    is_admin = False
    user_skills = []
    if g.user and session.get('user_id',False):
        is_admin = User(g.db).is_admin(session['user_id'])
            
        recs = User(g.db).get_roles(session['user_id'])
        if recs:
            user_skills = [rec.id for rec in recs]
            if not is_admin:
                #may be task admin
                for rec in recs:
                    if rec.rank >= 90: #activity manager
                        is_admin = True
                        break
                    pass
            
    if not user_skills:
        # user the default skills required
        user_skill_list = get_app_config().get('DEFAULT_USER_ROLES',['volunteer','user'])
        for skill in user_skill_list:
            rec = Role(g.db).get(skill)
            if rec:
                user_skills.append(rec.id)
                
    if not user_skills:
        raise ValueError("Could not determine user_skills")
    
    tasks = Task(g.db).query(sql)
    
    if tasks:
        for row in range(len(tasks)-1,-1,-1):
            """ First, delete any tasks that this user won't be able to see. 
            'Turkey Shoot' loop from end to first
            """
            task = tasks[row]
            # if user does not have skills requried, delete the row
            task_skills = un_pack_string(task.skill_list)
            if len(task_skills) > 0:
                if not User(g.db).is_admin(g.user): #admins see all...
                    task_skills = [int(i) for i in task_skills.split(',')]
                    for skill in task_skills:
                        if skill not in user_skills:
                            del tasks[row]
                            continue
            
            # Location resolution...
            # task.act_loc_* and task.task_loc_* fields will all be populated for display
            
            # defaults
            act_default_loc = task_default_loc = ('tbd',None,None) # location unkonown
            
            if task.act_loc_name and task.unique_task_locations == 0:
                task_default_loc = (task.act_loc_name, task.act_loc_lat, task.act_loc_lng)
                
            if not task.act_loc_name and task.unique_task_locations == 1:
                # location only in one task, set all to that loc
                task_loc_rec = Task(g.db).select_one(where = 'activity_id = {} and location_id notnull'.format(task.activity_id))
                if task_loc_rec:
                    loc_rec = Location(g.db).get(task_loc_rec)
                    if loc_rec:
                        act_default_loc = task_default_loc = (loc_rec.name, loc_rec.lat, loc_rec.lng)
                        
            if not task.act_loc_name and task.unique_task_locations > 0:
                # More than one location specifed
                act_default_loc = ('Multiple Locatons',None,None)
                    
            # use defaults if needed
            if task.act_loc_name == None:
                task.act_loc_name, task.act_loc_lat, task.act_loc_lng = act_default_loc
            if task.task_loc_name == None:
                task.task_loc_name, task.task_loc_lat, task.task_loc_lng = task_default_loc
                        
            #poplulate participant initials in list
            if g.user:
                #if not logged in, can't see any of this anyway...
                sql = """
                select user.id as user_id, upper(substr(user.first_name,1,1) || substr(user.last_name,1,1)) as initials 
                from user_task
                join user on user.id = user_task.user_id
                where user_task.task_id = {}
                order by user.first_name, user.last_name
                """.format(task.task_id)
                parts = Task(g.db).query(sql)
                task.participants = {}
                participant_list = []
                initials = []
                participant_skills = []
                if parts:
                    for part in parts:
                        if part.initials not in initials:
                            initials.append(part.initials)
                        if part.user_id not in participant_list:
                            participant_list.append(part.user_id)
                        
                    
                    task.participants[task.task_id] = {'initials':initials, 'users':participant_list,}
                    task.skill_list = un_pack_string(task.skill_list) # convert to simple list
            
            
    return render_template('signup_list.html',tasks=tasks,is_admin=is_admin)
        

@mod.route('/signup/<int:task_id>/',methods=['GET','POST',])
@mod.route('/signup/<int:task_id>',methods=['GET','POST',])
@mod.route('/signup',methods=['GET','POST',])
def signup(task_id=0):
    """Add or remove a signup
    May come from a modal dialog"""
    setExits()
    return "{} Task ID {}".format(g.title,task_id)
    
    