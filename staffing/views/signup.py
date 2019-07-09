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
    return redirect(url_for('.display'))
    
@mod.route('/about/')
@mod.route('/about')
def about():
    """So we can use www routes here"""
    g.title = "About"
    return render_template('about_signup.html')

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
@login_required
def more_info(activity_id=0):
    activity_id = cleanRecordID(activity_id)
    
    if activity_id > 0:
        g._more_info_activity_id = activity_id
        return display()
        
    return redirect(url_for('signup.display'))

@mod.route('/')
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
                
    start_date, end_date = get_display_date_range()
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
@login_required
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
        
    # get user_id
    user_id = None
    if 'user_id' in session:
        user_id = session['user_id']
        user = User(g.db).get(user_id)
        if not user:
            return 'failure: That is not a valid user id'
    else:
        redirect(abort(404))
        
    # setup for input form
    if job_id == None and request.form:
        job_id = request.form.get('id',-1)
        
    job_id = cleanRecordID(job_id)
    
    job = Job(g.db).get(job_id)
    if not job:
        return 'failure: That is not a valid job id'
    
    event = Event(g.db).get(job.event_id)
    if not event:
        return 'failure: That is not a valid event id'
            
    job_data = get_job_rows(None,None,"job.id = {}".format(job.id),[],is_admin=True)
    if job_data:
        job_data = job_data[0]
        filled_positions = job_data.job_filled_positions
        
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
    
    
    return render_template('signup_form.html',job=job,signup=signup,filled_positions=filled_positions)
    
    
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
                
    order_by = "sort_by_date_and_title" if as_spreadsheet else None
    
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
    
def get_display_date_range(days=None):
    """Return a tuple of the start and end dates for job display"""
    if not days:
        site_config = get_site_config()
        days = site_config.get('ROSTER_END_DAYS',30)
        
    start_date = local_datetime_now().isoformat()[:10]
    end_date = (local_datetime_now() + timedelta(days=days)).isoformat()[:10]
    return start_date, end_date


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
            
    volunteer_job_ids = get_job_ids_for_skills(default_skill_list)
        
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
        order_by = " activity_first_date, activity_title, job.start_date "
    
        
    sql = """
    select activity.id as activity_id, activity.title as activity_title, activity.description as activity_description, 
    event.id as event_id, 
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
    -- how many locations are speicifed for this event
    (select distinct coalesce(count(job.id),1) from job 
        where job.event_id = event.id and job.location_id not null and 
        job.location_id <> event.location_id and {where}) as unique_job_locations,
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
    0 as is_volunteer_job -- placeholder
    
    from job
    join event on event.id = job.event_id
    left join location as event_location on event_location.id = event.location_id
    left join location as job_location on job_location.id = job.location_id
    left join user as event_manager on event_manager.id = event.manager_user_id
    join activity on activity.id = event.activity_id
    left join client on client.id = event.client_id
    where {where}
    order by {order_by}
    """
    #print(sql.format(where=where, order_by=order_by,))
    #import pdb;pdb.set_trace()            
    jobs = Job(g.db).query(sql.format(where=where,order_by=order_by,))

    last_activity_id = 0
    dates_list = []
    if jobs:
        for job in jobs:
            # this only needs to run once for each activity id
            if job.activity_id != last_activity_id:
                last_activity_id = job.activity_id
                
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
                    
            job.event_date_list = dates_list
        
            # is this a job for a volunteer
            if str(job.job_id) in volunteer_job_ids:
                job.is_volunteer_job = 1
                
            # Location resolution...
            # job.event_loc_* and job.job_loc_* fields will all be populated for display
            # defaults
            job_default_loc = event_default_loc = ('tbd',None,None) # location unkonown
            job_default_loc_street_address = event_default_loc_street_address = ''
            job_default_loc_city = event_default_loc_city = ''
            job_default_loc_state = event_default_loc_state = ''
            job_default_loc_zip = event_default_loc_zip = ''
            
            if job.event_loc_name:
                # Set the job default loc to event loc
                job_default_loc = event_default_loc = (job.event_loc_name, job.event_loc_lat, job.event_loc_lng)
                job_default_loc_street_address = event_default_loc_street_address = job.event_loc_street_address
                job_default_loc_city =  event_default_loc_city = job.event_loc_city
                job_default_loc_state = event_default_loc_state = job.event_loc_state
                job_default_loc_zip = event_default_loc_zip = job.event_loc_zip
            
            if not job.event_loc_name and job.unique_job_locations == 1:
                # location only in one job, set all to that loc
                job_loc_rec = Job(g.db).select_one(where = 'event_id = {} and location_id not null'.format(job.event_id))
                if job_loc_rec:
                    loc_rec = Location(g.db).get(job_loc_rec.location_id)
                    if loc_rec:
                        event_default_loc = job_default_loc = (loc_rec.location_name, loc_rec.lat, loc_rec.lng)
                        event_default_loc_street_address = loc_rec.street_address
                        event_default_loc_city = loc_rec.city
                        event_default_loc_state = loc_rec.state
                        event_default_loc_zip = loc_rec.zip
                    
            if not job.event_loc_name and job.unique_job_locations > 1:
                # More than one location specifed
                event_default_loc = ('Multiple Locations',None,None)
                
            # use defaults if needed
            if job.event_loc_name == None or job.unique_job_locations > 0:
                job.event_loc_name, job.event_loc_lat, job.event_loc_lng = event_default_loc
                job.event_loc_street_address = job_default_loc_street_address
                job.event_loc_city = job_default_loc_city
                job.event_loc_state = job_default_loc_state
                job.event_loc_zip = job_default_loc_zip
                
            if job.job_loc_name == None:
                job.job_loc_name, job.job_loc_lat, job.job_loc_lng = job_default_loc
                job.job_loc_street_address = job_default_loc_street_address
                job.job_loc_city = job_default_loc_city
                job.job_loc_state = job_default_loc_state
                job.job_loc_zip = job_default_loc_zip
                    
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
    