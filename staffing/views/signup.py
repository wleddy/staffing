from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.shotglass import get_app_config
from shotglass2.takeabeltof.utils import render_markdown_for, render_markdown_text, printException, cleanRecordID, looksLikeEmailAddress, formatted_phone_number
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString, local_datetime_now
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.users.models import Role, User
from shotglass2.users.views.login import authenticate_user, setUserStatus, logout as log_user_out
from staffing.models import Event, Location, Job, UserJob
from staffing.utils import pack_list_to_string, un_pack_string


mod = Blueprint('signup',__name__, template_folder='templates/signup')


def setExits():
    g.listURL = url_for('.display')
    g.title = 'Signup'


@mod.route('/')
def display():
    """List Signup opportuniies"""
    setExits()
    app_config = get_app_config()
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
                #may be job admin
                for rec in recs:
                    if rec.rank >= app_config.get('MINIMUM_MANAGER_RANK',70): #event manager
                        is_admin = True
                        break
            
    #all visitors get basic skills even if not logged in
    user_skill_list = app_config.get('DEFAULT_USER_ROLES',['volunteer','user'])
    for skill in user_skill_list:
        rec = Role(g.db).get(skill)
        if rec and rec.id not in user_skills:
            user_skills.append(rec.id)
                
    where = "date(job.start_date) >= date('{}')".format(local_datetime_now().isoformat()[:10],)
    jobs = get_job_rows(where,user_skills,is_admin)
            
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
    app_config = get_app_config()
    job=None
    signup = None
    event = None
    user = None
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
            
    job_data = get_job_rows("job.id = {}".format(job.id),is_admin=True)
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
            from shotglass2.takeabeltof.mailer import send_message
            
            if positions > 0 and not previous_positions:
                # if adding first slot, send email with ical attachement
                #import pdb;pdb.set_trace()
                # generate the ical text #### the new signup record must exist so I can create a UID
                uid='{}_{}_{}'.format(
                    '000000{}'.format(event.id)[-6:],
                    '000000{}'.format(job.id)[-6:],
                    '000000{}'.format(user.id)[-6:],
                    )
                location = None
                description = event.description + '\n\n' + job.description
                if job_data.job_loc_name:
                    location = job_data.job_loc_name
                    description += '\n\n*location:*\n\n{}'.format(job_data.job_loc_name)

                if  job_data.job_loc_street_address and job_data.job_loc_city and job_data.job_loc_state:
                    description += '\n\n{}  {}'.format(', '.join([job_data.job_loc_street_address, job_data.job_loc_city]), job_data.job_loc_state.upper())

                map_url = None
                geo = None
                w3w = None
                if job_data.job_loc_w3w:
                    map_url = 'https://w3w.co/{}'.format(job_data.job_loc_w3w)
                    
                if job_data.job_loc_lat and job_data.job_loc_lng:

                    ### Apple Calender does not seem to use geo to set map location
                    ### it uses the value in location to try a reverse geocode lookup
                    geo = (job_data.job_loc_lat,job_data.job_loc_lng)
                        
                    #########################
                    #### for inital Testing
                    ########################
                    if app_config['DEBUG']:
                        geo = (37.386013,-122.082932)
                    
                    # Create a mapping uri
                    ############################
                    ## TODO - This should place a pin at least
                    ##        Maybe try to use apple maps if on iOS
                    ############################
                    if not map_url:
                        # don't replace the w3w link
                        map_url = "https://www.google.com/maps/place/@{},{},17z".format(geo[0],geo[1])
                    
                if map_url:
                    description = description + '\n\n' + 'Map: {}'.format(map_url)
                
                cal_desc = None
                if description:
                    cal_desc = description.replace('\n\n','\n') #remove teh double returns that markdown needs
                    
                ical_event = make_event_dict(uid,job.start_date,job.end_date,job.title,
                        description=cal_desc,
                        location=location,
                        geo=geo,
                        )
                    
                ical = cal(event=ical_event)

                # generate the text of the email with ical as an attachment
                email_html = render_markdown_for('announce/email/signup_announce.md',
                    bp=mod,
                    ical=ical,
                    description=description,
                    job_data=job_data,
                    )
                subject = 'Your assignment for {}'.format(event.title)
                attachment = None
                if ical:
                    attachment = ("{}.ics".format(job.title.replace(' ','_')), "text/calendar", ical)
                        
                # send that puppy!
                send_result = send_message([(user.email,' '.join([user.first_name,user.last_name]))],
                                subject=subject,
                                body_is_html=True,
                                body=email_html,
                                attachment=attachment,
                                )
                if not send_result[0]:
                    #Error occured
                    send_message(None,body="An error occored while trying to send signup email. Err: {}".format(send_result[1]))
                        
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
    
    
    return render_template('signup_form.html',job=job,event=event,signup=signup,filled_positions=filled_positions)
    
    
@mod.route('/signup_success/<int:id>/',methods=['GET','POST',])
@mod.route('/signup_success/<int:id>',methods=['GET','POST',])
@mod.route('/signup_success/',methods=['GET','POST',])
def signup_success(id=0):
    """Return a single row of job with the just updated data"""
    #import pdb;pdb.set_trace()
    id = cleanRecordID(id)
    
    # because the user got access to this job from the main display,
    # Set is_admin to true to display the updated version of the record
    jobs = get_job_rows("job.id = {}".format(id),is_admin=True)
    
    if jobs and len(jobs) > 0:
        job = jobs[0]
    else:
        return "failure: Job Not Found"
        
    return render_template('signup_job.html',job=job,show_detail=True)
    
    
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

def populate_participant_list(job):
    """Add participant values to the job namedlist"""
    sql = """
    select user.id as user_id, upper(substr(user.first_name,1,1) || substr(user.last_name,1,1)) as initials 
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
    if parts:
        for part in parts:
            if part.initials not in initials:
                initials.append(part.initials)
            if part.user_id not in participant_list:
                participant_list.append(part.user_id)
            
        
        job.participants[job.job_id] = {'initials':initials, 'users':participant_list,}
        job.skill_list = un_pack_string(job.skill_list) # convert to simple list
    
    
    
def get_job_rows(where,user_skills=[],is_admin=False):
    sql = """
    select event.id as event_id, event.title as event_title, event.description as event_description,
    event_location.id as event_loc_id,
    event_location.location_name as event_loc_name,
    event_location.street_address as event_loc_street_address,
    event_location.city as event_loc_city,
    event_location.state as event_loc_state,
    event_location.zip as event_loc_zip,
    event_location.lat as event_loc_lat,
    event_location.lng as event_loc_lng,
    event_location.w3w as event_loc_w3w,
    (select datetime(job.start_date) from job where job.event_id = event.id 
        order by datetime(job.start_date) limit 1 ) as active_first_date, 
    (select coalesce(sum(user_job.positions),0) from user_job
        where user_job.job_id in (select id from job where job.event_id = event.id)) as event_filled_positions,
    
    (select coalesce(sum(job.max_positions),1) from job 
        where job.event_id = event.id) as event_max_positions,
    (select distinct coalesce(count(job.id),1) from job 
        where job.event_id = event.id and job.location_id not null and 
        job.location_id <> event.location_id) as unique_job_locations,
    job.id as job_id,
    job.title as job_title,
    job.description as job_description,
    job.start_date,
    job.end_date,
    job.max_positions,
    job.skill_list,
    job_location.id as job_loc_id,
    job_location.location_name as job_loc_name,
    job_location.street_address as job_loc_street_address,
    job_location.city as job_loc_city,
    job_location.state as job_loc_state,
    job_location.zip as job_loc_zip,
    job_location.lat as job_loc_lat,
    job_location.lng as job_loc_lng,
    job_location.w3w as job_loc_w3w,

    null as participants, -- just a place holder
    (select coalesce(sum(user_job.positions),0) from user_job 
        where job.id = user_job.job_id and job.event_id = event.id) as job_filled_positions
    from job
    join event on event.id = job.event_id
    left join location as event_location on event_location.id = event.location_id
    left join location as job_location on job_location.id = job.location_id
    where {}
    order by active_first_date, job.start_date
    """
    
    jobs = Job(g.db).query(sql.format(where))

    if jobs:
        for row in range(len(jobs)-1,-1,-1):
            """ First, delete any jobs that this user won't be able to see. 
            'Turkey Shoot' loop from end to first
            """
            job = jobs[row]
            # if user does not have skills requried, delete the row
            job_skills = un_pack_string(job.skill_list)
            if len(job_skills) > 0:
                if not is_admin: #User(g.db).is_admin(g.user): #admins see all...
                    job_skills = [int(i) for i in job_skills.split(',')]
                    for skill in job_skills:
                        if skill not in user_skills:
                            del jobs[row]
                            continue
        
            # Location resolution...
            # job.event_loc_* and job.job_loc_* fields will all be populated for display
            #import pdb;pdb.set_trace()
            # defaults
            event_default_loc = job_default_loc = ('tbd',None,None) # location unkonown
            event_default_loc_street_address = ''
            event_default_loc_city = ''
            event_default_loc_state = ''
            event_default_loc_zip = ''
            event_default_loc_w3w = ''
            
            job_default_loc_street_address = ''
            job_default_loc_city = ''
            job_default_loc_state = ''
            job_default_loc_zip = ''
            job_default_loc_w3w = ''
        
            if job.event_loc_name:
                # Set the job default loc to event loc
                job_default_loc = (job.event_loc_name, job.event_loc_lat, job.event_loc_lng)
                job_default_loc_street_address = job.event_loc_street_address
                job_default_loc_city = job.event_loc_city
                job_default_loc_state = job.event_loc_state
                job_default_loc_zip = job.event_loc_zip
                job_default_loc_w3w = job.event_loc_w3w
            
            if not job.event_loc_name and job.unique_job_locations == 1:
                # location only in one job, set all to that loc
                job_loc_rec = Job(g.db).select_one(where = 'event_id = {} and location_id notnull'.format(job.event_id))
                if job_loc_rec:
                    loc_rec = Location(g.db).get(job_loc_rec)
                    if loc_rec:
                        event_default_loc = job_default_loc = (loc_rec.name, loc_rec.lat, loc_rec.lng)
                        event_default_loc_street_address = loc_rec.street_address
                        event_default_loc_city = loc_rec.city
                        event_default_loc_state = loc_rec.state
                        event_default_loc_zip = loc_rec.zip
                        event_default_loc_w3w = loc_rec.w3w
                    
            if job.unique_job_locations > 0:
                # More than one location specifed
                event_default_loc = ('Multiple Locations',None,None)
                
            # use defaults if needed
            if job.event_loc_name == None or job.unique_job_locations > 0:
                job.event_loc_name, job.event_loc_lat, job.event_loc_lng = event_default_loc
                job.event_loc_street_address = job_default_loc_street_address
                job.event_loc_city = job_default_loc_city
                job.event_loc_state = job_default_loc_state
                job.event_loc_zip = job_default_loc_zip
                job.event_loc_w3w = job_default_loc_w3w
                
            if job.job_loc_name == None:
                job.job_loc_name, job.job_loc_lat, job.job_loc_lng = job_default_loc
                job.job_loc_street_address = job_default_loc_street_address
                job.job_loc_city = job_default_loc_city
                job.job_loc_state = job_default_loc_state
                job.job_loc_zip = job_default_loc_zip
                job.job_loc_w3w = job_default_loc_w3w
                    
            if g.user:
                #if not logged in, can't see any of this anyway...
                populate_participant_list(job)
                
    return jobs
    
    
def cal(**kwargs):
    """Return the text of an icalendar object or None"""
    import random
    from icalendar import Calendar, Event
    #import pdb;pdb.set_trace()
    
    event = kwargs.get('event',None) # a dict of event data
    events = kwargs.get('events',None) # a list of event dicts
    out = None
    
    if events:
        if not isinstance(events,list):
            events = [events]
        events.extend([event])
    elif event:
        events = [event]
    
    calendar = Calendar()
    calendar.add('version','2.0')
    calendar.add('calscale','GREGORIAN')
    calendar.add('prodid','net.williesworkshop.calendar')
    calendar.add('x-priamry-calendar','TRUE')
    
    event_count = 0
    for event in events:
        if event:
            ev = Event()
            
            minumum_properties = True
            # Minimum required properties
            for key in ['uid','dtstart','dtend','summary',]:
                if key not in event:
                    minumum_properties = False
                    break
                value = event.pop(key)
                if isinstance(value,str) and key in ['dtstart','dtend',]:
                    value = getDatetimeFromString(value)
                    
                ev.add(key,value)
                
            if not minumum_properties:
                break
                
            for key, value in event.items():
                if value:
                    ev.add(key,value)
                
            ev.add('DTSTAMP',local_datetime_now('UTC'))
            calendar.add_component(ev)
            event_count += 1
            
    if event_count > 0:
        out = calendar.to_ical()
    
    return out
    
    
def make_event_dict(uid,start,end,summary,**kwargs):
    """Return a dictionary suitable for use when creating a calendar event"""
    ical_event = {}
    # the required fields
    ical_event['uid'] = uid
    ical_event['dtstart'] = start
    ical_event['dtend'] = end
    ical_event['summary'] = summary
    
    for key, value in kwargs.items():
        ical_event[key] = value
        
    return ical_event
    
