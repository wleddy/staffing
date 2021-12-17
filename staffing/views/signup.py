from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.shotglass import get_site_config
from shotglass2.takeabeltof.mailer import email_admin
from shotglass2.takeabeltof.utils import render_markdown_for, render_markdown_text, printException, cleanRecordID, looksLikeEmailAddress, formatted_phone_number
from shotglass2.takeabeltof.jinja_filters import excel_date_and_time_string
from shotglass2.takeabeltof.views import TableView
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString, local_datetime_now
from shotglass2.takeabeltof.jinja_filters import default_if_none
from shotglass2.takeabeltof.mailer import Mailer
from shotglass2.users.admin import login_required, table_access_required, silent_login
from shotglass2.users.models import Role, User, Pref
from shotglass2.users.views.login import authenticate_user, setUserStatus, logout as log_user_out, login as log_user_in
from shotglass2.www.views.home import contact as home_contact
from staffing.models import Event, Location, Job, UserJob, JobRole, Activity
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
    """Delegate the actual contact function to wwww"""
    return home_contact()

@mod.route('/contact_event_manager/<job_id>', methods=['GET','POST',])
@mod.route('/contact_event_manager/<job_id>/', methods=['GET','POST',])
@mod.route('/contact_event_manager/', methods=['GET','POST',])
def contact_event_manager(job_id=''):
    """User wants to contact the event manager"""
    
    #import pdb;pdb.set_trace()
    
    job_id = cleanRecordID(job_id)
    job_data = get_job_rows(None,None,'job.id = {}'.format(job_id),is_admin=True)
    if job_data:
        job_data = job_data[0]
        custom_message = render_markdown_for('announce/email/contact_event_manager_message.md',job_data=job_data,bp=mod)
        to_addr=""
        to_contact=""
        if job_data.event_manager_email:
            to_addr=job_data.event_manager_email
            to_contact="{} {}".format(job_data.event_manager_first_name,job_data.event_manager_last_name)
        subject='Contact regarding job: {}'.format(job_data.job_title)
        
        return home_contact(
            subject=subject,
            to_addr=to_addr,
            to_contact=to_contact,
            custom_message = custom_message,
            )
    
    email_admin(
        subject="Error contacting Event Manager",
        message="No job found in signup.contact_event_manager. job_id = {}".format(job_id),
    )
    flash("Sorry: Could not find the information for your request.")
    return redirect('/')
    
    
@mod.route('/help/')
@mod.route('/help')
def help():
    # send to sphinx help system
    return redirect('/help/index.html')
    
    
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
@mod.route('/signup/signup/<int:job_id>',methods=['GET','POST',])
@mod.route('/signup/signup/<int:job_id>/',methods=['GET','POST',])
@mod.route('/signup/signup',methods=['GET','POST',])
@mod.route('/signup/<int:job_id>',methods=['GET','POST',])
@mod.route('/signup/<int:job_id>/',methods=['GET','POST',])
@mod.route('/signup',methods=['GET','POST',])
@mod.route('/signup/',methods=['GET','POST',])
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

    if event.is_past_event:
        # this event is past
        return 'failure: No changes allowed. The event has already happened.'

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
        positions = cleanRecordID(request.form.get('positions',0))
        previous_positions = signup.positions
        submission_ok = True # set for success
        if signup.id and positions <= 0 and signup.id > 0:
            positions = -1 # indicates a cancellation of all positions
            UserJob(g.db).delete(signup.id)
            g.db.commit()
            
        # record change
        if positions > 0:
            
            # ensure that there are still some slots available...
            ###  it could happen that someone has signed up since the user
            ###  loaded the signup page
            if Job(g.db).filled(job_id) + positions <= Job(g.db).max_positions(job_id):
                UserJob(g.db).update(signup,request.form)
                signup.user_id = user_id
                signup.job_id = job_id
                signup.modified = local_datetime_now()
                UserJob(g.db).save(signup)
                g.db.commit()
                
            else:
                # all positions are filled. Someone signed up since the page loaded
                submission_ok = False
                # not really 'success', but an appropreate message will be displayed
                return 'success' 
            
        if submission_ok:
            # send some notices
            
            if positions > 0 and not previous_positions:
                # if adding first slot, send email with ical attachement
                #import pdb;pdb.set_trace()
                
                send_signup_email(job_data,user,'announce/email/signup_announce.md',mod,escape=False)
                         
            # send an email to the Event manager as appropriate
            send_manager_signup_notice(
                positions=positions,
                previous_positions=previous_positions,
                job_data=job_data,
                user=user,
                )

            return 'success'
    
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
    
    
@mod.route('/acknowledge_signup/<int:id>',methods=['GET','POST',])
@mod.route('/acknowledge_signup/<int:id>/',methods=['GET','POST',])
@mod.route('/acknowledge_signup/',methods=['GET','POST',])
def acknowledge_signup(id=0):
    """Send a dialog to confirm the users signup choice"""
    
    uj = UserJob(g.db).select(where="user_id = {} and job_id = {}".format(session.get('user_id',-1),cleanRecordID(id)))
    user_signed_up = uj != None
    
    signup_status = "success"
    if not uj:
        signup_status = 'full'
        
    return render_template('signup_acknowledgment.html',signup_status=signup_status)
        
@mod.route('/delete_position',methods=['GET',])
@mod.route('/delete_position/',methods=['GET',])
def acknowledge_deletion():
    """Send a dialog after user cancels a position"""
    
    signup_status = "cancel"

    return render_template('signup_acknowledgment.html',signup_status=signup_status)


@mod.route('/roster/<int:display_end_days>',methods=['GET','POST',])
@mod.route('/roster/<int:display_end_days>/',methods=['GET','POST',])
@mod.route('/roster',methods=['GET',])
@mod.route('/roster/',methods=['GET','POST',])
@table_access_required(Job)
def roster(display_end_days=0):
    """Display the roster of events.
    Allows for search by date or pre-set periods
    """
    
    # import pdb;pdb.set_trace()
    
    BEGINNING_OF_TIME = datetime(1000,1,1)
    END_OF_TIME = datetime(4000,12,31)
        
    setExits()
    g.title='Signup Roster'
    site_config = get_site_config()
    # get the current users role id's
    is_admin = is_user_admin()
    end_date = start_date = local_datetime_now()
    try:
        display_end_days = int(request.form.get('display_end_days',request.args.get('display_end_days',0)))
    except:
        display_end_days = 0
        
    as_spreadsheet = False
    if request.method == "GET":
        # on the inital GET see if the as_spreadsheet option is set in session
        as_spreadsheet = session.get("roster_as_spreadsheet",False)
    else:
        # is POST
        if "as_spreadsheet" in request.form:
            as_spreadsheet = True
    
    session["roster_as_spreadsheet"] = as_spreadsheet
    
    
    if display_end_days < 0:
        #Use the date input fields for search
        temp_date = getDatetimeFromString(request.form.get('roster_start_date',date_to_string(BEGINNING_OF_TIME,'iso_date')))
        # if not temp_date:
#             temp_date = BEGINNING_OF_TIME
        start_date = temp_date
        
        temp_date = getDatetimeFromString(request.form.get('roster_end_date',date_to_string(END_OF_TIME,'iso_date')))
        # if not temp_date:
 #            temp_date = END_OF_TIME
        end_date = temp_date
    elif display_end_days > 0:
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
                
    order_by = " sort_by_date_and_title, is_volunteer_job, start_date" 
    
    jobs = get_job_rows(start_date,end_date,"",user_skills,is_admin,order_by=order_by)
    
    return render_template('roster.html',
        jobs=jobs,
        is_admin=is_admin,
        display_end_days=display_end_days,
        as_spreadsheet=as_spreadsheet,
        start_date=start_date,
        end_date=end_date,
        )
    

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
    event.status as event_status,
    (select case when '{today}' > event.event_start_date then 1 else 0 end) as is_past_event,
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
    null as event_header_location_name, -- a placeholder
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
    coalesce((select 1 from job_role where job_role.role_id in ({vol_role_ids}) and job_role.job_id = job.id),0) as is_volunteer_job
    
    
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
    sql = sql.format(
                where=where,
                order_by=order_by,
                group_by=group_by,
                vol_role_ids=vol_role_ids,
                today=date_to_string(local_datetime_now(),'iso_date_tz'),
            )
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
                
                # need to set this each time the activity changes in the list
                activity_location_name = 'tbd'
                activity_locations = get_activity_location_list(job.activity_id,where)
                if activity_locations:
                    if len(activity_locations) == 1:
                        activity_location_name = activity_locations[0].location_name
                    elif len(activity_locations) > 1:
                        activity_location_name = "Multiple Locations"
         
                job.activity_loc_name = activity_location_name
                
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
            
            # Location resolution...
            # job.event_loc_* and job.job_loc_* fields will all be populated for display
            # defaults
            job.event_header_location_name = default_if_none(job.event_loc_name,'tdb')
            event_default_loc = (job.event_header_location_name, job.event_loc_lat, job.event_loc_lng)
            event_default_loc_street_address = default_if_none(job.event_loc_street_address,'')
            event_default_loc_city = default_if_none(job.event_loc_city,'')
            event_default_loc_state = default_if_none(job.event_loc_state,'')
            event_default_loc_zip = default_if_none(job.event_loc_zip,'')
            event_default_loc_id = default_if_none(job.event_loc_id,None)
            
            # get unique location list for event related to this job
            event_locations = Event(g.db).locations(job.event_id)
                
            # import pdb;pdb.set_trace()
            if event_locations:
                if len(event_locations) > 1:
                    job.event_header_location_name = 'Multiple Locations'
                else:
                    if event_locations[0].id == job.job_loc_id:
                        # there is only one location and it is not the event location
                        # use the job location for the event location
                        event_default_loc = (job.job_loc_name, job.job_loc_lat, job.job_loc_lng)
                        event_default_loc_street_address = job.job_loc_street_address
                        event_default_loc_city = job.job_loc_state
                        event_default_loc_zip = job.job_loc_zip
                        event_default_loc_id = job.job_loc_id
                
                # finally, set the event and job locations if not already
                if not job.job_loc_name:
                    job.job_loc_name, job.job_loc_lat, job.job_loc_lng = event_default_loc
                    job.job_loc_street_address = event_default_loc_street_address
                    job.job_loc_city = event_default_loc_city
                    job.job_loc_state = event_default_loc_state
                    job.job_loc_zip = event_default_loc_zip
                    job.job_loc_id = event_default_loc_id
            
                if not job.event_loc_name:
                    job.event_loc_name, job.event_loc_lat, job.event_loc_lng = event_default_loc
                    job.event_loc_street_address = event_default_loc_street_address
                    job.event_loc_city = event_default_loc_city
                    job.event_loc_state = event_default_loc_state
                    job.event_loc_zip = event_default_loc_zip
                    job.event_loc_id = event_default_loc_id

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
    """Get a selection of location records or None for this activity but limited
    to only the jobs in the current signup selection"""
    
    if where_clause:
        where_clause = " and " + where_clause
        
    activity_location_list = []
        
    sql = """
    select distinct event.location_id as event_loc_id, job.location_id as job_loc_id from event
    left join job on job.event_id = event.id
    join activity on activity.id = event.activity_id
    where event.activity_id = {activity_id} {where_clause}
    """.format(activity_id=cleanRecordID(activity_id),where_clause=where_clause)
    
    recs = Event(g.db).query(sql)
    
    loc_ids = set()
    if recs:
        for rec in recs:
            if rec.job_loc_id:
                loc_ids.add(rec.job_loc_id)
            elif rec.event_loc_id:
                loc_ids.add(rec.event_loc_id)
                    
    if loc_ids:
        return Location(g.db).select(where='id in ({})'.format(','.join(str(x) for x in loc_ids)))
    
    return None
    
        
def get_volunteer_role_ids():
    #get the ids for vounteer roles
    l= ['"' + x + '"' for x in get_site_config().get('DEFAULT_USER_ROLES',['volunteer','user'])]
    vol_roles = Role(g.db).select(where="name in ({})".format(",".join(l)))
    vol_role_ids = ''
    if vol_roles:
        vol_role_ids = ",".join([str(x.id) for x in vol_roles])
    
    return vol_role_ids
    
    
def get_staff_user_ids():
    """Return a text string cotaining the user ids of those users with a staff role.
    The string is suitable for use in a SQL "in" query.
    The Role selection is based on rank. Staff are to have a rank >= 50 and <=100
    """
    
    sql = """select user.* 
    from user
    join user_role on user_role.user_id = user.id 
    join role on role.id = user_role.role_id 
    where role.rank >= 50 and role.rank <=100
    
    """
    recs = Role(g.db).query(sql)
    out = '0' # will create a ligit query, but no results
    if recs:
        y = set([str(rec.id) for rec in recs])
        out = ",".join(set([str(rec.id) for rec in recs]))
    
    return out
    
    
@mod.route('/get_commitment_email/<user_name_or_email>/',methods=['GET',])
@mod.route('/get_commitment_email/<user_name_or_email>',methods=['GET',])
@mod.route('/get_commitment_email/',methods=['GET',])
def send_user_commitment_email(user_name_or_email=None):
    """Send an email to the user with all their future commitments
    
    Param: user_name_or_email : the user_name or email address
    """
    
    #import pdb;pdb.set_trace()
    
    result = "No Result Yet"
    
    # get the user record
    user = User(g.db).get(user_name_or_email)
    if user:
        # get all the job.id's for user's future jobs
        sql = """
            select user_job.user_id, user_job.job_id from user_job
            join job on user_job.job_id = job.id
        
            where user_job.user_id = {user_id} and date(job.start_date,'localtime') >= '{today}'
        """.format(user_id=user.id,today=date_to_string(local_datetime_now(),'iso_date'))
        user_jobs = UserJob(g.db).query(sql)
    
        job_data = None
        jobs_list = None
        if user_jobs:
            jobs_list = ','.join([str(x.job_id) for x in user_jobs])
        if jobs_list:
            job_data = get_job_rows(None,None,"job.id in ({})".format(jobs_list),[],is_admin=True)
        if job_data:

            try:
                send_signup_email(job_data,
                    user,
                    'announce/email/commitment_reminder.md',
                    mod,
                    escape=False,
                    subject="Your Commitments for {}".format(get_site_config()["SITE_NAME"]),
                    renminder_type="future",
                    )
            
                result = 'Your commitment report has been emailed to you.'
            
            except Exception as e:
                mes = "An error occurred while sending user commitment email. Err: {}".format(str(e))
                email_admin(mes,printException(mes))
            
                result = "Sorry: Something wierd happened and we were not able to send an email. We'll look into it."
        else:
            result =  'Sorry: No Future Commitments found.'
    else:
        # no user record found
        result = "Sorry: Could not find the user record."
        
        
    return render_template('get_commitment_result.html',result=result)
    
    

@mod.route('/volunteer_contacts',methods=['GET',])
@mod.route('/volunteer_contacts/',methods=['GET',])
@table_access_required(User)
def volunteer_contact_list():
    """A cvs export of a contact list of volunteers who worked a shift in the last 12 months"""
    
    report_start_date = local_datetime_now() - timedelta(days=365)
    
    sql = """
    with 
        vols as (select id from role where name = 'volunteer' or name = 'user'), 
        not_vols as (select id from role where id not in (select id from vols))

        -- The first query finds any user who has ever signed up for a volunteer shift
        select user.id, user.first_name, user.last_name, user.first_name || ' ' || user.last_name as full_name, 
        user.email, user.phone, user.address, user.address2, user.city, user.state, user.zip, user.active
        from user_job
        join job on job.id = user_job.job_id and date(job.start_date) >= date('{report_start_date}')
        join user on user.id = user_job.user_id
        join job_role on job_role.job_id = user_job.job_id
        where
            user_job.job_id in (select job_role.job_id from job_role where job_role.role_id in (select id from vols))
            -- and date(job.start_date) >= date('{report_start_date}')
        group by user.id

        -- ### this includes anyone who ever volunteered, we dont want that now ###
        -- union
        -- 
        -- -- This query finds any user who has only 'user' or 'volunteer' roles regardless of if they ever worked a shift
        -- select user.id, user.first_name, user.last_name, user.first_name || ' ' || user.last_name as full_name, 
        -- user.email, user.phone, user.address, user.address2, user.city, user.state, user.zip, user.active
        -- from user_role
        -- left join user on user.id = user_role.user_id
        -- where
        --     user_role.role_id not in (select id from not_vols)
        -- group by user.id

        intersect

        -- only select active users
        select user.id, user.first_name, user.last_name, user.first_name || ' ' || user.last_name as full_name, 
        user.email, user.phone, user.address, user.address2, user.city, user.state, user.zip, user.active
        from user where user.active == 1
        order by user.last_name collate nocase, user.first_name collate nocase;
    """.format(report_start_date = str(report_start_date))

    recs = User(g.db).query(sql)
    if recs:
        view = TableView(User,g.db)
        view.export_fields = [
            {'name':'first_name'},
            {'name':'last_name'},
            {'name':'full_name'},
            {'name':'email'},
            {'name':'phone'},
            {'name':'address'},
            {'name':'address2'},
            {'name':'city'},
            {'name':'state'},
            {'name':'zip'},
            {'name':'active'},
        ]
        view.list_fields = view.export_fields
        view.recs = recs
        view.export_file_name = 'volunteer_contact_list.csv'
        view.export_title = "Volunteer Contact List for {} thru {}\n".format(
                    date_to_string(report_start_date,'date'),
                    date_to_string(local_datetime_now(),'date')
                )
    
        return view.export()
    
    
            
    flash("No Volunteers Found")
    return redirect(url_for('www.home'))
    
def send_manager_signup_notice(**kwargs):
    """Send an email to the event manager if user signed up close to the date of the event"""

    positions = kwargs.get('positions',0)
    previous_positions = kwargs.get("previous_positions",0)
    job_data = kwargs.get('job_data',None)
    user = kwargs.get("user",None)
        
    days_pref = Pref(g.db).get("Alert on Signup",
            default=2,
            description="""When a user signs up or cancels within this many days before an event an email is sent to the Event Manager.
Enter the number of days or -1 to always be notified""",
            user_name = get_site_config().get('HOST_NAME',None),
            )
    days = int(days_pref.value)
    
    if not user or not job_data or not job_data.event_manager_user_id:
        return # there is no point in going on

    if days < 0 or local_datetime_now() >= getDatetimeFromString(job_data.start_date) - timedelta(days=days):
        # Alert the event manager
        mailer = Mailer(**kwargs)
        mailer.add_address((job_data.event_manager_email,' '.join([job_data.event_manager_first_name,job_data.event_manager_last_name])))
        mailer.subject = "Signup Change for {job_title} at {calendar_title}".format(calendar_title=job_data.calendar_title,job_title=job_data.job_title)
        mailer.body_is_html = True
        mailer.html_template = 'email/signup_change.html'
    
        mailer.send()
        if not mailer.success:
            #Error occured
            email_admin(subject="Error sending job change notice at {}".format(get_site_config()['SITE_NAME']),message="An error occored while trying to send job change email. Err: {}".format(mailer.result_text))
    
    return
