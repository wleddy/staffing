from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.shotglass import get_app_config
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID, looksLikeEmailAddress, formatted_phone_number
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString, local_datetime_now
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.users.models import Role, User
from shotglass2.users.views.login import authenticate_user, setUserStatus, logout as log_user_out
from staffing.models import Activity, Location, Task, UserTask
from staffing.utils import pack_list_to_string, un_pack_string


mod = Blueprint('signup',__name__, template_folder='templates/signup')


def setExits():
    g.listURL = url_for('.display')
    g.title = 'Signup'


@mod.route('/')
def display():
    """List Signup opportuniies"""
    setExits()
    
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
            
    #all visitors get basic skills even if not logged in
    user_skill_list = get_app_config().get('DEFAULT_USER_ROLES',['volunteer','user'])
    for skill in user_skill_list:
        rec = Role(g.db).get(skill)
        if rec and rec.id not in user_skills:
            user_skills.append(rec.id)
                
    where = "date(task.start_date) >= date('{}')".format(local_datetime_now().isoformat()[:10],)
    tasks = get_task_rows(where,user_skills,is_admin)
            
    return render_template('signup_list.html',tasks=tasks,is_admin=is_admin)
        

@mod.route('/signup/<int:task_id>/',methods=['GET','POST',])
@mod.route('/signup/<int:task_id>',methods=['GET','POST',])
@mod.route('/signup',methods=['GET','POST',])
def signup(task_id=None):
    """Add or remove a signup
    May come from a modal dialog"""
    setExits()
    task=None
    signup = None
    activity = None
    filled_positions = 0
    
    # if user not logged in, get that first
    #import pdb;pdb.set_trace()
    if not g.user:
        next = request.url
        rec = User(g.db).new()
        return render_template('signup_login.html',rec=rec,next=next,submit_script = 'submitModalToModalForm',from_main=0)
    
    # get user_id
    user_id = None
    if 'user_id' in session:
        user_id = session['user_id']
    else:
        redirect(abort(404))
    # setup for input form
    if task_id == None and request.form:
        task_id = request.form.get('id',-1)
        
    task_id = cleanRecordID(task_id)
    
    task = Task(g.db).get(task_id)
    if not task:
        return 'failure: That is not a valid task id'
        
    # get the user's signup
    signup = UserTask(g.db).select_one(where='user_id = {} and task_id = {}'.format(user_id,task_id))
    if not signup:
        signup = UserTask(g.db).new()
        
        
    # if submitting form record signup
    if request.form:
        positions = cleanRecordID(request.form.get('positions',0))
        if positions > 0 and signup.positions == 0:
            # if adding first slot, send email with ical attachement
            pass
            
        if positions < signup.positions:
            # the number of positions has been reduced
            pass
            # if reducing committment and < 2 days to task,
            #.   If is staff... inform activity manager and email staff that they need to find a replacement?
            #.   if not staff, inform activity manager and record change
            # if reducing and not within 2 days
            #   if not staff, just record the change
            #   if Staff, Inform activity manager
        if signup.id and positions <= 0 and signup.id > 0:
            UserTask(g.db).delete(signup.id)
            g.db.commit()
            return 'success'
                
        # record change
        if positions > 0:
            UserTask(g.db).update(signup,request.form)
            signup.user_id = user_id
            signup.task_id = task_id
            signup.modified = local_datetime_now()
            UserTask(g.db).save(signup)
            g.db.commit()
        return 'success'
    
    
    return render_template('signup_form.html',task=task,activity=activity,signup=signup,filled_positions=filled_positions)
    
@mod.route('/signup_success/<int:id>/',methods=['GET','POST',])
@mod.route('/signup_success/<int:id>',methods=['GET','POST',])
@mod.route('/signup_success/',methods=['GET','POST',])
def signup_success(id=0):
    """Return a single row of task with the just updated data"""
    #import pdb;pdb.set_trace()
    id = cleanRecordID(id)
    
    # because the user got access to this task from the main display,
    # Set is_admin to true to display the updated version of the record
    tasks = get_task_rows("task.id = {}".format(id),is_admin=True)
    
    if tasks and len(tasks) > 0:
        task = tasks[0]
    else:
        return "failure: Task Not Found"
        
    return render_template('signup_task.html',task=task,show_detail=True)
    
    
@mod.route('/login',methods=['GET','POST',])
@mod.route('/login/<int:from_main>',methods=['GET','POST',])
@mod.route('/login/',methods=['GET','POST',])
def login(from_main=0):
    # no password is required for volunteer login
    setExits()
    ready_to_login = False
    password_required = False
    #import pdb;pdb.set_trace()
    if g.user:
        log_user_out()
        
    if not 'first_pass' in session:
        session['first_pass'] = True
    else:
        session['first_pass'] = False
        
    first_pass = session['first_pass']
    
    user_rec = User(g.db).get(request.form.get('email','').strip())
    if user_rec:
        ready_to_login = True
        # Check for a password
        user_password = request.form.get('login_password')
        if user_rec.password:
            if not user_password:
                # redisplay the form with a password box
                ready_to_login = False
                password_required = True
                flash("You must enter your password.")
            else:
                #validate the user login
                if authenticate_user(user_rec.email,user_password) > 0:
                    #User is logged in
                    ready_to_login = True
                else:
                    ready_to_login = False
                    flash("Password did not match your record")
                    password_required = True
    else:
        if not from_main or not first_pass:
            flash("Could not find your account")

    if ready_to_login:
        # login user without a password if they don't have one
        log_user_out()
        setUserStatus(user_rec.email,user_rec.id)
        return 'success'
        
    # Redisplay form
    rec = User(g.db).new()
    submit_script = 'submitModalToModalForm'
    next = "/page-not-found/"
    if from_main:
        submit_script = 'submitModalForm'
        next = g.listURL
        
    if request.form:
        User(g.db).update(rec,request.form)
        next=request.form.get('next',next)
        
    return render_template('signup_login.html',rec=rec,next=next,password_required=password_required,submit_script=submit_script,from_main=from_main)
    

@mod.route('/logout',methods=['GET',])
@mod.route('/logout/',methods=['GET',])
def logout():
    setExits()
    log_user_out()
    return redirect(g.listURL)


@mod.route('/register',methods=['GET','POST',])
@mod.route('/register/<int:from_main>',methods=['GET','POST',])
@mod.route('/register/',methods=['GET','POST',])
def register(from_main=0):
    """Allow volunteers to create an account"""
    setExits()
    ready_to_login = True
    next=request.form.get('next','/page-not-found/')
    rec = User(g.db).new()
    
    # all fields are required
    required_fields = ['first_name','last_name','email','phone']
    for key, value in request.form.items():
        if key in required_fields and not value:
            flash("All fields are required")
            ready_to_login = False
            break
    
    User(g.db).update(rec,request.form)
    #import pdb;pdb.set_trace()
    
    # email address must look like one...
    if ready_to_login:
        if not looksLikeEmailAddress(rec.email):
            flash("{} doesn't look like an email address".format(rec.email))
            ready_to_login = False
    # Check the phone number
    if ready_to_login:
        formatted_phone = formatted_phone_number(rec.phone)
        if not formatted_phone:
            flash("{} doesn't look like an phone number. Be sure to include the area code".format(rec.phone))
            ready_to_login = False
        else:
            rec.phone = formatted_phone
    # test that email address is not in use
    if ready_to_login:
        test_user = User(g.db).get(rec.email)
        if test_user:
            flash("Someone with that email address (probably you) is already registered. Try login in instead")
            ready_to_login = False
    # create account and log user in
    if ready_to_login:
        User(g.db).save(rec)
        # Try to give the user a couple roles
        role = Role(g.db).get('volunteer')
        if role:
            User(g.db).add_role(rec.id,role.id)
        role = Role(g.db).get('user')
        if role:
            User(g.db).add_role(rec.id,role.id)
        g.db.commit()
        log_user_out()
        setUserStatus(rec.email,rec.id)
        return "success"
        
        
    submit_script = 'submitModalToModalForm'
    if from_main:
        submit_script = 'submitModalForm'
        next = g.listURL

    return render_template('signup_login.html',rec=rec,next=next,register=True,submit_script=submit_script,from_main=from_main)

def populate_participant_list(task):
    """Add participant values to the task namedlist"""
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
    
    
    
def get_task_rows(where,user_skills=[],is_admin=False):
    sql = """
    select activity.id as activity_id, activity.title as activity_title, activity.description as activity_description,
    act_location.id as act_loc_id,
    act_location.location_name as act_loc_name,
    act_location.lat as act_loc_lat,
    act_location.lng as act_loc_lng,
    (select datetime(task.start_date) from task where task.activity_id = activity.id 
        order by datetime(task.start_date) limit 1 ) as active_first_date, 
    (select coalesce(sum(user_task.positions),0) from user_task
        where user_task.task_id in (select id from task where task.activity_id = activity.id)) as activity_filled_positions,
    
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
    where {}
    order by active_first_date, task.start_date
    """
    
    tasks = Task(g.db).query(sql.format(where))

    if tasks:
        for row in range(len(tasks)-1,-1,-1):
            """ First, delete any tasks that this user won't be able to see. 
            'Turkey Shoot' loop from end to first
            """
            task = tasks[row]
            # if user does not have skills requried, delete the row
            task_skills = un_pack_string(task.skill_list)
            if len(task_skills) > 0:
                if not is_admin: #User(g.db).is_admin(g.user): #admins see all...
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
                # The only loctation speicied is in the Activity Record
                task_default_loc = (task.act_loc_name, task.act_loc_lat, task.act_loc_lng)
            
            if not task.act_loc_name and task.unique_task_locations == 1:
                # location only in one task, set all to that loc
                task_loc_rec = Task(g.db).select_one(where = 'activity_id = {} and location_id notnull'.format(task.activity_id))
                if task_loc_rec:
                    loc_rec = Location(g.db).get(task_loc_rec)
                    if loc_rec:
                        act_default_loc = task_default_loc = (loc_rec.name, loc_rec.lat, loc_rec.lng)
                    
            if task.unique_task_locations > 0:
                # More than one location specifed
                act_default_loc = ('Multiple Locations',None,None)
                
            # use defaults if needed
            if task.act_loc_name == None or task.unique_task_locations > 0:
                task.act_loc_name, task.act_loc_lat, task.act_loc_lng = act_default_loc
            if task.task_loc_name == None:
                task.task_loc_name, task.task_loc_lat, task.task_loc_lng = task_default_loc
                    
            if g.user:
                #if not logged in, can't see any of this anyway...
                populate_participant_list(task)
                
    return tasks
