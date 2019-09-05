from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.shotglass import get_site_config
from shotglass2.takeabeltof.mailer import send_message
from shotglass2.takeabeltof.utils import render_markdown_for, render_markdown_text, printException, cleanRecordID, looksLikeEmailAddress, formatted_phone_number
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString, local_datetime_now
from shotglass2.users.admin import login_required, table_access_required, silent_login
from shotglass2.users.models import Role, User
from shotglass2.users.views.login import authenticate_user, setUserStatus, logout as log_user_out, login as log_user_in
from shotglass2.www.views.home import contact as home_contact
from staffing.models import Event, Location, Job, UserJob, JobRole
from staffing.views.announcements import send_signup_email, process_commitment_reminder
from datetime import timedelta, datetime

mod = Blueprint('signup',__name__, template_folder='templates/signup')


def setExits():
    g.listURL = url_for('.display')
    g.title = 'Volunteer Signup'
    
@mod.route('/home/', methods=['GET','POST',])
def home():
    """So we can use www routes in this blueprint"""
    return display()
    return redirect(url_for('.display'))
    
# @mod.route('/about/')
# @mod.route('/about')
# def about():
#     """So we can use www routes here"""
#     g.title = "About"
#     return render_template('about_signup.html')

@mod.route('/contact/', methods=['GET','POST',])
@mod.route('/contact', methods=['GET','POST',])
def contact():
    """Delecate the actual contact function to wwww"""
    return home_contact()

@mod.route('/help/')
@mod.route('/help')
def help():
    return "No help yet"
    
    
@mod.route('/more_info')
@mod.route('/more_info/')
@mod.route('/more_info/<int:activity_id>/')
def more_info(activity_id=0):
    activity_id = cleanRecordID(activity_id)
    
    # if not g.user:
    #     ## get login first
    #     flash("You need to log in or create an account")
    #     return redirect(url_for('login.login')+ '?next={}{}'.format(url_for('signup.more_info'),activity_id))
        
    if activity_id > 0:
        g._more_info_activity_id = activity_id
        return display()
        
    return redirect(url_for('signup.display'))

@mod.route('/activities/')
def display():
    """List Signup opportuniies"""
    setExits()
    site_config = get_site_config()
    #import pdb;pdb.set_trace()
    # get the current users role id's
    is_admin = False
    user_skills = []
    recs = User(g.db).get_roles(session.get('user_id',-1))
    if recs:
        user_skills = [rec.id for rec in recs]
        
    is_admin = is_user_admin()
            
    #all visitors get basic skills even if not logged in
    user_skill_list = site_config.get('DEFAULT_USER_ROLES',['volunteer','user'])
    for skill in user_skill_list:
        rec = Role(g.db).get(skill)
        if rec and rec.id not in user_skills:
            user_skills.append(rec.id)
                
    start_date = local_datetime_now().isoformat()[:10]
    end_date = None # forever...
    
    where = ''
    activity_id = g.get('_more_info_activity_id',0)
    if activity_id:
        where = 'activity.id = {}'.format(activity_id)
    
    jobs = get_job_rows(start_date,end_date,where,user_skills,is_admin)
            
    return render_template('signup_list.html',jobs=jobs,is_admin=is_admin)
        

############################
##### The "passenger" WSGI system on A2 hosting may be why
#####.   the extra 'signup/signup' routes are needed.
##### I could almost swear that this worked ok at one time.
###########################
@mod.route('/signup/signup/<int:job_id>/',methods=['GET','POST',])
@mod.route('/signup/signup/<int:job_id>',methods=['GET','POST',])
@mod.route('/signup/signup',methods=['GET','POST',])
@mod.route('/signup/<int:job_id>/',methods=['GET','POST',])
@mod.route('/signup/<int:job_id>',methods=['GET','POST',])
@mod.route('/signup/',methods=['GET','POST',])
@mod.route('/signup',methods=['GET','POST',])
def signup(job_id=None):
    """Add or remove a signup
    May come from a modal dialog"""
    setExits()
    site_config = get_site_config()
    job=None
    signup = None
    event = None
    user = None
    filled_positions = 0
    job_id = cleanRecordID(request.form.get('id',job_id))
        
    job_data = get_job_rows(None,None,"job.id = {}".format(job_id),[],is_admin=True)
    if job_data:
        job_data = job_data[0]
        filled_positions = job_data.job_filled_positions
    else:
        return'failure: That is not a valid job id'
        
    event = Event(g.db).get(job_data.event_id)
    if not event:
        return 'failure: That is not a valid event id'

    if not g.user:
        ## get login first
        flash("You need to log in or create an account")
        return redirect(url_for('login.login')+ '?next={}{}'.format(url_for('signup.more_info'),event.activity_id))
        
    # get user_id
    user_id = None
    if 'user_id' in session:
        user_id = session['user_id']
        user = User(g.db).get(user_id)
        if not user:
            return 'failure: That is not a valid user id'
    else:
        redirect(abort(404))
        
    # get the user's signup
    signup = UserJob(g.db).select_one(where='user_id = {} and job_id = {}'.format(user_id,job_id))
    if not signup:
        signup = UserJob(g.db).new()
        
        
    # if submitting form record signup
    if request.form:
        #import pdb;pdb.set_trace()
        positions = cleanRecordID(request.form.get('positions',0))
        previous_positions = signup.positions
        submission_ok = True # set for success
        if signup.id and positions <= 0 and signup.id > 0:
            positions = -1 # indicates a cancellation of all positions
            UserJob(g.db).delete(signup.id)
            g.db.commit()
                
        # record change
        if positions > 0:
            ##################
            # TODO - Don't allow any change after the day of the event...
            ###################
            UserJob(g.db).update(signup,request.form)
            signup.user_id = user_id
            signup.job_id = job_id
            signup.modified = local_datetime_now()
            UserJob(g.db).save(signup)
            g.db.commit()
            
        if submission_ok:
            # send some notices
            
            if positions > 0 and not previous_positions:
                # if adding first slot, send email with ical attachement
                #import pdb;pdb.set_trace()
                
                send_signup_email(job_data,user,'announce/email/signup_announce.md',mod,escape=False)
                         
            if previous_positions and positions < previous_positions:
                # the number of positions has been reduced
                pass
                # Dont allow reduction after the date of the event
                #
                # if reducing committment and < 2 days to job,
                #.   If is staff... inform event manager and email staff that they need to find a replacement?
                #.   if not staff, inform event manager and record change
                # if reducing and not within 2 days
                #   if not staff, just record the change
                #   if Staff, Inform event manager
            
        if submission_ok:
            return 'success'
        else:
            # return the form with flashed message?
            pass
    
    
    return render_template('signup_form.html',job=job_data,signup=signup,filled_positions=filled_positions)
    
    
@mod.route('/signup_success/<int:id>/',methods=['GET','POST',])
@mod.route('/signup_success/<int:id>',methods=['GET','POST',])
@mod.route('/signup_success/',methods=['GET','POST',])
def signup_success(id=0):
    """Return a single row of job with the just updated data"""
    #import pdb;pdb.set_trace()
    id = cleanRecordID(id)
    
    # because the user got access to this job from the main display,
    # Set is_admin to true to display the updated version of the record
    jobs = get_job_rows(None,None,"job.id = {}".format(id),[],is_admin=True)    
    if jobs and len(jobs) > 0:
        job = jobs[0]
    else:
        return "failure: Job Not Found"
        
    return render_template('signup_job.html',job=job,is_admin=is_user_admin())
    
    
@mod.route('/acknowledge_signup/<int:id>/',methods=['GET','POST',])
@mod.route('/acknowledge_signup/<int:id>',methods=['GET','POST',])
@mod.route('/acknowledge_signup/',methods=['GET','POST',])
def acknowledge_signup(id=0):
    """Send a dialog to confirm the users signup choice"""
    
    uj = UserJob(g.db).select(where="user_id = {} and job_id = {}".format(session.get('user_id',-1),cleanRecordID(id)))
    user_signed_up = uj != None
    
    return render_template('signup_acknowledgment.html',user_signed_up=user_signed_up)
        
    
@mod.route('/roster/<int:display_end_days>',methods=['GET','POST',])
@mod.route('/roster/<int:display_end_days>/',methods=['GET','POST',])
@mod.route('/roster',methods=['GET',])
@mod.route('/roster/',methods=['GET','POST',])
@table_access_required(Job)
def roster(display_end_days=0):
    """Display the roster of all current events
    for now, define current as jobs that occure on today or within the next 2 weeks.
    """
    
    #import pdb;pdb.set_trace()
    
    setExits()
    g.title='Signup Roster'
    site_config = get_site_config()
    # get the current users role id's
    is_admin = is_user_admin()
    end_date = start_date = local_datetime_now()
    display_end_days = cleanRecordID(request.form.get('display_end_days',request.args.get('display_end_days',0)))
    as_spreadsheet=request.form.get("as_spreadsheet",False)
    
    if display_end_days > 0:
        end_date = end_date + timedelta(days=display_end_days)
    elif display_end_days < 0:
        #display all future events
        end_date = end_date + timedelta(days=2000) # that ought to do it...
    
    user_skills = []
    recs = User(g.db).get_roles(session.get('user_id',-1))
    if recs:
        user_skills = [rec.id for rec in recs]
                
    #all visitors get basic skills even if not logged in
    user_skill_list = site_config.get('DEFAULT_USER_ROLES',['volunteer','user'])
    for skill in user_skill_list:
        rec = Role(g.db).get(skill)
        if rec and rec.id not in user_skills:
            user_skills.append(rec.id)
                
    order_by = " sort_by_date_and_title, is_volunteer_job, start_date" 
    
    jobs = get_job_rows(start_date,end_date,"",user_skills,is_admin,order_by=order_by)
    return render_template('roster.html',jobs=jobs,is_admin=is_admin,display_end_days=display_end_days,as_spreadsheet=as_spreadsheet,)
    

@mod.route('/process_notifications',methods=['GET','POST',])
@mod.route('/process_notifications/',methods=['GET','POST',])
@silent_login()
def process_notifications():
    """Send Reminders and notifications to Volunteers and Staff
    
    Designed to be called by a chron job or other means. The 'staff_notification' table is
    used to record when a particular notification was sent to a user so that re-running
    method will not send it more than once.
    
    Notification functions are responsible for determining if a notification should be sent
    and updating the staff_notification table as needed.
    
    This function will not attempt to process any request received 'in the middle of the night'.
    """
    
    #import pdb;pdb.set_trace()
    
    now = local_datetime_now()
    
    # send between 9am and 9pm only
    if now.hour >= 9 and now.hour <= 21:
        process_commitment_reminder()
        
    return 'Ok' #Always Ok
        
        
def populate_participant_list(job):
    """Add participant values to the job namedlist"""
    sql = """
    select user.id as user_id, upper(substr(user.first_name,1,1) || substr(user.last_name,1,1)) as initials,
    (user.first_name || ' '  || user.last_name ) as user_name, user.phone as phone, user.email as email,
    user_job.positions
    from user_job
    join user on user.id = user_job.user_id
    where user_job.job_id = {}
    order by user.first_name, user.last_name
    """.format(job.job_id)
    parts = Job(g.db).query(sql)
    job.participants = {}
    participant_list = []
    initials = []
    participant_skills = []
    user_data_list = []
    if parts:
        for part in parts:
            if part.initials not in initials:
                initials.append(part.initials)
            if part.user_id not in participant_list:
                participant_list.append(part.user_id)
                user_data_list.append({'user_name':part.user_name,'phone':part.phone,'email':part.email,'positions':part.positions,})
            
        job.participants[job.job_id] = {'initials':initials, 'users':participant_list, 'user_data': user_data_list}
    

def is_user_admin():
    is_admin = False
    if g.user and session.get('user_id',False):
        is_admin = User(g.db).is_admin(session['user_id'])
            
        if not is_admin:
            site_config = get_site_config()
            #may be job admin
            recs = User(g.db).get_roles(session['user_id'])
            if recs:
                for rec in recs:
                    if rec.rank >= site_config.get('MINIMUM_MANAGER_RANK',70): #event manager
                        is_admin = True
                        break
    
    return is_admin

def get_job_rows(start_date=None,end_date=None,where='',user_skills=[],is_admin=False,**kwargs):
    """
    Make a row list for job and event records

    where = some text for the basic where cluase. May be augmented by additional parameters
    user_skills = a list of role id values. Limit the display of jobs users with these roles may see.
    start_date = first job start_date to include
    end_date = last job end_date to include
    is_admin = is the current user an administrator for the purposes of this selection.
    
    Query happens in 2 steps, first find the jobs that require the skills in user_skills,
    Then use that selection to reduce the list of jobs to just those jobs.
    """
    
    site_config = get_site_config()
    
    #import pdb;pdb.set_trace()
    user_id = session.get('user_id',0)
    
    # from this point, use date strings
    if isinstance(start_date,datetime):
        start_date = start_date.isoformat()[:10]
    elif not start_date:
        start_date = '1970-01-01'
    if isinstance(end_date,datetime):
        end_date = end_date.isoformat()[:10]
    elif not end_date:
        end_date = '2051-02-08'
        
    ## Don't use 'localtime' modifier with date strings without timezone info
    where_date_range = " and date(job.start_date, 'localtime') >= date('{}') and date(job.start_date, 'localtime') <= date('{}') ".format(start_date,end_date)
        
    event_status_where = " " + kwargs.get('event_status_where'," and lower(event.status) = 'scheduled' ") + " "
    
    def get_job_ids_for_skills(skill_ids):
        """Return a list of job.id (as strings) where the jobs have one or more of skills required"""
        the_job_ids = []
        if skill_ids:
            job_roles = JobRole(g.db).select(where="role_id in ({})".format(','.join([str(x) for x in skill_ids])))
            if job_roles:
                the_job_ids = [str(x.job_id) for x in job_roles]
                
        return the_job_ids
            
    # get a list of basic user skills
    default_skills = site_config.get('DEFAULT_USER_ROLES',['volunteer','user'])
    default_skill_list = []
    for skill in default_skills:
        rec = Role(g.db).get(skill)
        if rec and rec.id not in default_skill_list:
            default_skill_list.append(rec.id)
            
    volunteer_skills = "0"
    if default_skill_list:
        volunteer_skills = '{}'.format(','.join([str(x) for x in default_skill_list]))
        
    where_skills = ''
    if is_admin:
        # admins see everything
        pass
    else:
        #limit selection by user skills
                
        #get a list of job ids for all jobs that can be done by volunteers
        volunteer_jobs_list = []
        
        if not user_skills:
            #visitors get basic skills even if not logged in
            user_skills = default_skill_list
            
        # limit job selection to only jobs the user can do
        job_ids = get_job_ids_for_skills(user_skills)
        
        if job_ids:
            where_skills = ' and job.id in ({})'.format(','.join(job_ids))
        
    if not where:
        where = "1 "
    
    where = where + event_status_where + where_date_range + where_skills

    order_by = kwargs.get('order_by',None)
    if not order_by:
        order_by = " activity_first_date, activity_title, substr(job.start_date,1,10), is_volunteer_job, job.start_date "
    
    group_by = kwargs.get('group_by','')
    if group_by:
        group_by = 'group by {}'.format(group_by)
        
    vol_role_ids = get_volunteer_role_ids()
    
    sql = """
    select activity.id as activity_id, 
    activity.title as activity_title, 
    activity.description as activity_description,
    activity.activity_type_id,
    null as activity_loc_name,
    coalesce(nullif(event.service_type,''),(select type from activity_type where activity_type.id = activity.activity_type_id ),"Activity Type") as service_type,
    event.id as event_id,
    event.event_start_date,
    event.event_end_date,
    event.event_start_date_label_id,
    coalesce((select label from event_date_label where id = event.event_start_date_label_id ),'Event Start') as event_start_label,
    event.event_end_date_label_id,
    coalesce((select label from event_date_label where id = event.event_end_date_label_id ),'Event End') as event_end_label,
    event.service_start_date,
    event.service_end_date,
    event.service_start_date_label_id,
    coalesce((select label from event_date_label where id = event.service_start_date_label_id ),'Service Start') as service_start_label,
    event.service_end_date_label_id,
    coalesce((select label from event_date_label where id = event.service_end_date_label_id ),'Service End') as service_end_label,
    coalesce(nullif(event.calendar_title,''),activity.title) as calendar_title,
    event.exclude_from_calendar,
    coalesce(nullif(event.description,''),activity.description) as event_description,
    -- get contact info client table if available else event table
    coalesce(nullif(event.client_contact,''),event.client_contact) as event_client_contact,
    coalesce(nullif(event.client_email,''),event.client_email) as event_client_email,
    coalesce(nullif(event.client_phone,''),event.client_phone) as event_client_phone,
    coalesce(nullif(event.client_website,''),event.client_website) as event_client_website,
    -- get contact from event table if available, else client table
    (select coalesce(nullif(event.client_contact,''),client.contact_first_name | " " | client.contact_last_name)) as client_contact,
    (select coalesce(nullif(event.client_email,''),client.email)) as client_email,
    (select coalesce(nullif(event.client_phone,''),client.phone)) as client_phone,
    (select coalesce(nullif(event.client_website,''),client.website)) as client_website,
    event.staff_info as event_staff_info,
    event_manager.id as event_manager_user_id,
    event_manager.first_name as event_manager_first_name,
    event_manager.last_name as event_manager_last_name,
    event_manager.email as event_manager_email,
    event_manager.phone as event_manager_phone,
    event_location.id as event_loc_id,
    event_location.location_name as event_loc_name,
    event_location.street_address as event_loc_street_address,
    event_location.city as event_loc_city,
    event_location.state as event_loc_state,
    event_location.zip as event_loc_zip,
    event_location.lat as event_loc_lat,
    event_location.lng as event_loc_lng,
    null as event_date_list, -- a list of dates for this event
    -- used to sort spreadsheet view
    substr(job.start_date,1,10) || activity.title as sort_by_date_and_title,
    -- the first date of any job for this event
    (select min(job.start_date) from job where job.event_id = event.id and {where}) as event_first_date, 
    -- the first date of any job for this activity
    (select min(job.start_date) from job join event on event.id = job.event_id where event.activity_id = activity.id and {where}) as activity_first_date, 
    -- the number of positions filled in this event
    (select coalesce(sum(user_job.positions),0) from user_job
        where user_job.job_id in (select id from job where job.event_id = event.id and {where} )) as event_filled_positions,
    -- the total positions for this event
    (select coalesce(sum(job.max_positions),1) from job 
        where job.event_id = event.id and {where}) as event_max_positions,
    -- the number of positions filled in this activity
    (select coalesce(sum(user_job.positions),0) from user_job
        where user_job.job_id in (select id from job where job.event_id in (select event.id from event where event.activity_id = activity.id) and {where} )) as activity_filled_positions,
    -- the total positions for this activity
    (select coalesce(sum(job.max_positions),1) from job 
        where job.event_id in (select event.id from event where event.activity_id = activity.id ) and {where}) as activity_max_positions,
    job.id as job_id,
    job.title as job_title,
    event.status as event_status,
    coalesce(job.description,'') as job_description,
    job.start_date,
    job.end_date,
    job.max_positions,
    job_location.id as job_loc_id,
    job_location.location_name as job_loc_name,
    job_location.street_address as job_loc_street_address,
    job_location.city as job_loc_city,
    job_location.state as job_loc_state,
    job_location.zip as job_loc_zip,
    job_location.lat as job_loc_lat,
    job_location.lng as job_loc_lng,

    null as participants, -- just a place holder
    0 as user_event_positions,
    0 as user_job_positions,
    (select coalesce(sum(user_job.positions),0) from user_job 
        where job.id = user_job.job_id and job.event_id = event.id and {where}) 
        as job_filled_positions,
    -- 1 if a volunteer job, else 0
    coalesce((select 1 from job_role where job_role.role_id in ({vol_role_ids}) and job_role.job_id = job.id),0) as is_volunteer_job,
    coalesce(
        (select 1 from event where date(event.event_start_date,'localtime') < date('now','localtime') and event.id = job.event_id)
     ,0) 
    as is_past_event
    
    
    from job
    join event on event.id = job.event_id
    left join location as event_location on event_location.id = event.location_id
    left join location as job_location on job_location.id = job.location_id
    left join user as event_manager on event_manager.id = event.manager_user_id
    join activity on activity.id = event.activity_id
    left join client on client.id = event.client_id
    where {where}
    {group_by}
    order by {order_by}
    """
    sql = sql.format(where=where,order_by=order_by,group_by=group_by,volunteer_skills=volunteer_skills,vol_role_ids=vol_role_ids,)
    #print(sql)
    #import pdb;pdb.set_trace()            
    jobs = Job(g.db).query(sql)

    last_activity_id = 0
    dates_list = []
    if jobs:
        for job in jobs:

            # this only needs to run once for each activity id (assuming the records are in activity ID order)
            if job.activity_id != last_activity_id:
                last_activity_id = job.activity_id
                
                # clear the location names
                activity_location_name = None

                # Get a list location ids of all events and jobs for this activity
                activity_location_list = get_activity_location_list(job.activity_id,where)
                
                #import pdb;pdb.set_trace()
                               
                unique_activity_locations = len(activity_location_list)
                if unique_activity_locations > 1:
                    activity_location_name = "Multiple Locations"
                elif unique_activity_locations == 1:
                    activity_location_name = job.event_loc_name
                    if not activity_location_name:
                        act_loc = Location(g.db).get(activity_location_list[0])
                        if act_loc:
                            activity_location_name = act_loc.location_name
                        
                # generate a list of all dates of events for this activity in this selection of jobs
                # get a selection of jobs for this actvity's events
                sql = """
                select job.*, event.status from job 
                join event on event.id = job.event_id 
                where job.event_id in (select event.id from event where event.activity_id = {}) {} {} {} 
                order by job.start_date
                """.format(job.activity_id,where_date_range,where_skills,event_status_where)
                job_dates = Job(g.db).query(sql)
                #put into list
                dates_list = []
                if job_dates:
                    for job_date in job_dates:
                        if job_date.start_date[:10] not in dates_list:
                            dates_list.append(job_date.start_date[:10])
                    
            #import pdb;pdb.set_trace()
            job.event_date_list = dates_list
            
            job.activity_loc_name = activity_location_name
                    
            # Location resolution...
            # job.event_loc_* and job.job_loc_* fields will all be populated for display
            # defaults
            event_default_loc = ('tbd',None,None) # location unkonown
            event_default_loc_street_address = ''
            event_default_loc_city = ''
            event_default_loc_state = ''
            event_default_loc_zip = ''
            event_default_loc_id = None
            
            if job.event_loc_name:
                # Set the defaults to event loc
                event_default_loc = (job.event_loc_name, job.event_loc_lat, job.event_loc_lng)
                event_default_loc_street_address = job.event_loc_street_address
                event_default_loc_city = job.event_loc_city
                event_default_loc_state = job.event_loc_state
                event_default_loc_zip = job.event_loc_zip
                event_default_loc_id = job.event_loc_id
                
            elif job.job_loc_name:
                #set default to the job location
                event_default_loc = (job.job_loc_name, job.job_loc_lat, job.job_loc_lng)
                event_default_loc_street_address = job.job_loc_street_address
                event_default_loc_city = job.job_loc_city
                event_default_loc_state = job.job_loc_state
                event_default_loc_zip = job.job_loc_zip
                event_default_loc_id = job.job_loc_id
                
            
            # use defaults if needed
            if job.event_loc_name == None:
                job.event_loc_name, job.event_loc_lat, job.event_loc_lng = event_default_loc
                job.event_loc_street_address = event_default_loc_street_address
                job.event_loc_city = event_default_loc_city
                job.event_loc_state = event_default_loc_state
                job.event_loc_zip = event_default_loc_zip
                job.event_loc_id = event_default_loc_id
            
            if job.job_loc_name == None:
                job.job_loc_name, job.job_loc_lat, job.job_loc_lng = event_default_loc
                job.job_loc_street_address = event_default_loc_street_address
                job.job_loc_city = event_default_loc_city
                job.job_loc_state = event_default_loc_state
                job.job_loc_zip = event_default_loc_zip
                job.job_loc_id = event_default_loc_id
                    
            # if there are multiple locations for this event, set the event location info accordingly
            sql = """
            select job.location_id from event 
            join job on job.event_id = event.id
            where job.event_id ={event_id} and job.location_id <> event.location_id
            """.format(event_id=job.event_id)
            
            job_locs = Event(g.db).query(sql)
            
            event_location_count = 0
            if cleanRecordID(job.event_loc_id) > 0:
                event_location_count = 1
            if job_locs:
                for x in job_locs:
                    if x.location_id != job.event_loc_id:
                        event_location_count += 1
            
                if event_location_count > 1:
                    # set event to Multiple Locatons
                    job.event_loc_name, job.event_loc_lat, job.event_loc_lng = ('Multiple Locations',None,None) 
                    job.event_loc_street_address = ''
                    job.event_loc_city = ''
                    job.event_loc_state = ''
                    job.event_loc_zip = ''
                    job.event_loc_id = None
                                        

            if g.user:
                #if not logged in, can't see any of this anyway...
                populate_participant_list(job)
                
                
                    
            ##################
            ## There really ought to be a way to do these 2 queries within the main query
            ## but I can't figure it out
            ##################
            # set the number of positions the current user has for this job
            sql = """
            select coalesce(sum(user_job.positions),0) as temp from user_job
            where user_job.user_id = {} and user_job.job_id = {}
            
            """.format(user_id,job.job_id)
            UJPos = UserJob(g.db).query(sql)
            if UJPos:
                job.user_job_positions = UJPos[0].temp
                
            # set the number of positions the current user has for the event this job is a part of
            sql = """
            select coalesce(sum(user_job.positions),0) as temp from user_job
            join job on job.id = user_job.job_id
            where user_job.user_id = {} and job.event_id = {}
            """.format(user_id,job.event_id)
            UJPos = UserJob(g.db).query(sql)
            if UJPos:
                job.user_event_positions = UJPos[0].temp
            
    return jobs
    
    
def get_activity_location_list(activity_id,where_clause=''):
    """Get a list location ids of all events and jobs for this activity"""
    
    if where_clause:
        where_clause = " and " + where_clause
        
    sql = """
    select distinct event.location_id as event_loc_id, job.location_id as job_loc_id from event
    left join job on job.event_id = event.id
    join activity on activity.id = event.activity_id
    where event.activity_id = {activity_id} {where_clause}
    """.format(activity_id=cleanRecordID(activity_id),where_clause=where_clause)
    
    loc_recs = Job(g.db).query(sql)
    
    activity_location_list = []
    if not loc_recs:
        # no location set at all (this should never really happen...)
        activity_location_name = "tbd"
    else:
        for x in loc_recs:
            if x.event_loc_id and x.event_loc_id not in activity_location_list:
                activity_location_list.append(x.event_loc_id)
            if x.job_loc_id and x.job_loc_id not in activity_location_list:
                activity_location_list.append(x.job_loc_id)
    
    return activity_location_list
    
    
def get_volunteer_role_ids():
    #get the ids for vounteer roles
    l= ['"' + x + '"' for x in get_site_config().get('DEFAULT_USER_ROLES',['volunteer','user'])]
    vol_roles = Role(g.db).select(where="name in ({})".format(",".join(l)))
    vol_role_ids = ''
    if vol_roles:
        vol_role_ids = ",".join([str(x.id) for x in vol_roles])
    
    return vol_role_ids