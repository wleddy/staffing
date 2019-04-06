from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.users.models import Role, User
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString, local_datetime_now
from shotglass2.takeabeltof.mailer import email_admin
from shotglass2.shotglass import get_site_config
from staffing.models import Event, Location, Job, UserJob
from staffing.utils import pack_list_to_string, un_pack_string
from staffing.views.announcements import send_signup_email
from staffing.views.signup import get_job_rows

mod = Blueprint('job',__name__, template_folder='templates/job', url_prefix='/job')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Jobs'


@mod.route('/')
@table_access_required(Job)
def display():
    setExits()
    g.title="Event Job List"
    recs = Job(g.db).select()
    
    return render_template('job_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/<int:event_id>/',methods=['GET','POST',])
@table_access_required(Job)
def edit(id=0,event_id=0,edit_from_list=False):
    setExits()
    g.title = 'Edit Job Record'
    #import pdb;pdb.set_trace()
    
    job_date=None
    start_time=None
    start_time_AMPM=None
    end_time=None
    end_time_AMPM=None
    locations = Location(g.db).select()
    slots_filled = 0
    users = None
    
    if id == 0 and request.form:
        id = request.form.get('id',0)
        event_id = request.form.get('event_id',0)
    
    id = cleanRecordID(id)
    event_id = cleanRecordID(event_id)
    job = Job(g.db)
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = job.get(id)
        if not rec:
            flash("{} Record Not Found".format(job.display_name))
            return redirect(g.listURL)
        event_id = rec.event_id
        #slots_filled = job.slots_filled(rec.id)
        
    else:
        rec = job.new()
        if 'last_job' in session:
            # apply previous record
            ses_rec = session['last_job']
            for key,value in rec._asdict().items():
                if key != 'id' and key in ses_rec:
                    rec._update([(key,ses_rec[key])])
            
        rec.event_id = event_id
    
    current_event = Event(g.db).get(event_id)
    events = None
    if not current_event:
        events =  Event(g.db).select() # This should only return current or future events
    
    #import pdb;pdb.set_trace()
    
    roles = Role(g.db).select(where='name <> "admin" and name <> "super"')
    selected_roles = [] # this needs to be populated from JobRoles
    # get a list of users who can fill this job
    #users = Users(g.db).
        
    
    if request.form:
        job.update(rec,request.form)
        #rec.event_id = cleanRecordID(request.form.get("event_id"))
        if valid_input(rec):
            if cleanRecordID(rec.location_id) <= 0:
                rec.location_id = None
            
            job.save(rec)
            g.db.commit()
            session['last_job'] = rec._asdict()
            if edit_from_list:
                return 'success'
            return redirect(g.listURL)
        else:
            job_date=request.form.get('job_date',"")
            start_time=request.form.get('start_time',"")
            start_time_AMPM=request.form.get('start_time_AMPM',"AM")
            end_time=request.form.get('end_time',"")
            end_time_AMPM=request.form.get('end_time_AMPM',"AM")
    else:
        if rec.start_date and isinstance(rec.start_date,str):
            rec.start_date = getDatetimeFromString(rec.start_date)
        if rec.start_date:
            job_date=date_to_string(rec.start_date,'date')
            start_time=date_to_string(rec.start_date,'time')
            start_time_AMPM=date_to_string(rec.start_date,'ampm').upper()
        if rec.end_date and isinstance(rec.end_date,str):
            rec.start_date = getDatetimeFromString(rec.end_date)
        if rec.end_date:
            end_time=date_to_string(rec.end_date,'time')
            end_time_AMPM=date_to_string(rec.end_date,'ampm').upper()
            
    template = 'job_edit.html'
    if edit_from_list:
        template = 'job_embed_edit.html'
    
    return render_template(template,rec=rec,
            roles=roles,
            job_date=job_date,
            start_time=start_time,
            start_time_AMPM= start_time_AMPM,
            end_time=end_time,
            end_time_AMPM=end_time_AMPM,
            events=events,
            current_event=current_event,
            locations=locations,
            slots_filled=slots_filled,
            users=users,
            )
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(Job)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    job = Job(g.db)
    if id <= 0:
        return abort(404)
        
    rec = job.get(id)
        
    if rec:
        job.delete(rec.id)
        g.db.commit()
        #flash("Job {} Deleted from {}".format(rec.title,job.display_name))
    
    return redirect(g.listURL)
    
    
@mod.route('/edit_job_from_list/<int:id>/',methods=['GET','POST',])
@mod.route('/edit_job_from_list/<int:id>',methods=['GET','POST',])
@mod.route('/edit_job_from_list/<int:id>/<int:event_id>/',methods=['GET','POST',])
@mod.route('/edit_job_from_list/<int:id>/<int:event_id>',methods=['GET','POST',])
@mod.route('/edit_job_from_list/',methods=['GET','POST',])
@table_access_required(Job)
def edit_job_from_list(id=0,event_id=0):
    return edit(id,event_id,True)
    
@mod.route('/delete_from_list/<int:id>/',methods=['GET','POST',])
@mod.route('/delete_from_list/<int:id>',methods=['GET','POST',])
@mod.route('/delete_from_list/',methods=['GET','POST',])
@table_access_required(Job)
def delete_from_list(id=0):
    id = cleanRecordID(id)
    if id > 0:
        rec = Job(g.db).get(id)
        if rec:
            delete(id)
            return "success"
    return 'Could not find a Job with that ID'

    
@mod.route('/get_job_list_for_event/',methods=['GET','POST',])
@mod.route('/get_job_list_for_event/<int:id>/',methods=['GET','POST',])
@mod.route('/get_job_list_for_event/<int:id>',methods=['GET','POST',])
def get_job_list_for_event(id=0):
    """Return a fully formated html table for use in the Event edit form"""
    #import pdb;pdb.set_trace()
    id = cleanRecordID(id)
    #jobs = Job(g.db).select(where='event_id = {}'.format(id))
    job_data = get_job_rows(None,None,"job.event_id = {}".format(id),[],is_admin=True)
    
    return render_template('job_embed_list.html',jobs=job_data,event_id=id)
    
    
@mod.route('/manage/<int:id>/',methods=['GET','POST',])
@mod.route('/manage/<int:id>',methods=['GET','POST',])
@mod.route('/manage/',methods=['GET','POST',])
@table_access_required(Job)
def manage_job_set(id=None):
    """Duplicate, move or delete a set of jobs that share an event id and date"""
    
    #import pdb;pdb.set_trace()
    action = request.args.get('action')
    new_date=request.form.get('new_date')
    
    id = cleanRecordID(request.form.get('id',id))
    
    if id < 1:
        return 'failure: That is not a valid job ID'
        
    if action not in [None,'copy','move','delete',]:
        return 'failure: That is not a valid action request'
    
    job = Job(g.db)
    rec = job.get(id)
    if not rec:
        return "failure: Job not found."
        
    dup_date = None
    if request.form and action != 'delete':
        try:
            dup_date = coerce_datetime(request.form.get('new_date',''),'00:00:00')
            if dup_date:
                #convert it to a string
                dup_date = date_to_string(dup_date,'iso_date') #'YYYY-MM-DD'
            else:
                flash("That is not a valid date")
        except:
            flash("Got an error while processing the date")
            
    if request.form and (dup_date or action == 'delete'):
        recs = job.select(where="event_id = {} and date(start_date,'localtime') = date('{}','localtime')".format(rec.event_id,rec.start_date))
        if recs:
            for rec in recs:
                if action == 'delete':
                    job.delete(rec.id)
                else:
                    if action == 'copy':
                        rec.id = None
                        
                    rec.start_date = dup_date + rec.start_date[10:]
                    rec.end_date = dup_date + rec.end_date[10:]
                    job.save(rec)
    
            job.commit()

            return 'success'
        
    return render_template('job_manage.html',rec=rec,new_date=new_date)
    
    
@mod.route('/assignment_manager/<int:job_id>',methods=['GET',])
@mod.route('/assignment_manager/<int:job_id>/',methods=['GET',])
@mod.route('/assignment_manager',methods=['POST',])
@mod.route('/assignment_manager/',methods=['POST',])
@table_access_required(Job)
def assignment_manager(job_id=0):
    """Add or remove a signup initiated by a manager
    Comes from a modal dialog but unlike most times, this method will not close
    the dialog on "success". The Dlog remains open until the user cancels it."""
    
    setExits()
    site_config = get_site_config()
    job=None
    signup = None
    assigned_users = None
    filled_positions = None
    
    #import pdb;pdb.set_trace()

    #Get the job id
    if not job_id and request.form:
        job_id = request.form.get('id',None)
    
    # Sanatize job_id
    job_id = cleanRecordID(job_id)
    if job_id < 1:
        return "failure: That is not a valid job id"
        
    #if Post, create assignment
    if request.form:
        assignment_user_id = cleanRecordID(request.form.get('assignment_user_id',None))
        if assignment_user_id < 1:
            return "failure: You need to select a user first."
            
        if cleanRecordID(request.form.get('positions')) < 1:
            return "failure: The number of positions must be at least 1."
            
        signup = UserJob(g.db).select_one(where='user_id = {} and job_id = {}'.format(assignment_user_id,job_id))
        if not signup:
            signup = UserJob(g.db).new()
            signup.user_id = assignment_user_id
            signup.job_id = job_id
        
        UserJob(g.db).update(signup,request.form)
        signup.modified = local_datetime_now()
        UserJob(g.db).save(signup)
        g.db.commit()
        
        # send a special email to the user to inform them of the assignment.
        manager_rec = User(g.db).get(session.get('user_id',0))
        user_rec = User(g.db).get(assignment_user_id)
        # need a fresh copy of this
        job_data = get_job_rows(None,None,"job.id = {}".format(job_id),[],is_admin=True)
        if job_data:
            job_data = job_data[0]
            subject = "[SABA] {} {} has given you an assignment".format(manager_rec.first_name,manager_rec.last_name)
            send_signup_email(job_data,user_rec,'email/inform_user_of_assignment.html',mod,manager=manager_rec,subject=subject,job_data=job_data)
        else:
            # failed to get the job data... this should never happen
            email_admin(subject="Alert from {}".format(site_config['SITE_NAME']),
                message="Unable to send Manager Assignment email. 'job_data' is None? 'job_id' = {}, 'user_id'={}".format(job_id,assignment_user_id))
            flash("Unable to send email to user. (Err: job_data is None)")
        # The form is going to be redisplayed so clear the signup record
        signup = None

    if not signup:
        signup = UserJob(g.db).new()
        signup.job_id = job_id
        signup.positions=0
        
    #Get the job to display
    job_data = get_job_rows(None,None,"job.id = {}".format(job_id),[],is_admin=True)
    role_list=[0] #will return none
    if job_data:
        job_data = job_data[0]
        filled_positions = job_data.job_filled_positions
        # get skills for this job
        role_list = un_pack_string(job_data.skill_list) # convert to comma separated string
        role_list = role_list.split(',') #convert it to a list
    
    # Get all the users who can do this job
    skilled_users = User(g.db).get_with_roles(role_list)
        
    #get all users currently assigned
    assigned_users = UserJob(g.db).get_assigned_users(job_id)

    #remove users already assigned from skilled users
    if assigned_users:
        for au in assigned_users:
            if skilled_users:
                for i in range(len(skilled_users)):
                    if skilled_users[i].id == au.id:
                        del skilled_users[i]
                        break
        
    return render_template('assignment_manager.html',
            job=job_data,
            signup=signup,
            assigned_users=assigned_users,
            skilled_users=skilled_users,
            filled_positions=filled_positions,
            )

    
@mod.route('/assignment_manager_delete/<int:job_id>/<int:user_id>',methods=['GET',])
@mod.route('/assignment_manager_delete/<int:job_id>/<int:user_id>/',methods=['GET',])
@mod.route('/assignment_manager_delete/',methods=['GET',])
@table_access_required(Job)
def assignment_manager_delete(job_id=0,user_id=0):
    """Delete a job assignment"""
    setExits()
    site_config = get_site_config()
    
    #import pdb;pdb.set_trace()
    job_id = cleanRecordID(job_id)
    user_id = cleanRecordID(user_id)
    if job_id > 0 and user_id > 0:
        signup=UserJob(g.db).select_one(where='job_id = {} and user_id = {}'.format(job_id,user_id))
        if signup:
            UserJob(g.db).delete(signup.id)
            g.db.commit()

            job_data = get_job_rows(None,None,"job.id = {}".format(job_id),[],is_admin=True)
            if job_data:
                job_data = job_data[0]
                # send a special email to the user to inform them of the assignment.
                manager_rec = User(g.db).get(session.get('user_id',0))
                user_rec = User(g.db).get(user_id)
                subject = "[SABA] {} {} has cancelled your assignment".format(manager_rec.first_name,manager_rec.last_name)
                send_signup_email(job_data,user_rec,'email/inform_user_of_cancellation.html',mod,manager=manager_rec,subject=subject,job_data=job_data,no_calendar=True)
            else:
                # failed to get the job data... this should never happen
                email_admin(subject="Alert from {}".format(site_config['SITE_NAME']),
                    message="Unable to send Manager Cancellation email. 'job_data' is None? 'job_id' = {}, 'user_id'={}".format(job_id,user_id))
                flash("Unable to send email to user. (Err: job_data is None)")

            return assignment_manager(job_id)
            
        return "failure: User_Job record could not be found"
            
    return "failure: Invalid User or Job id"


def valid_input(rec):
    valid_data = True
    #import pdb;pdb.set_trace()
    
    job_title = request.form.get('title','').strip()
    if not job_title:
        valid_data = False
        flash("You must give the job a title")
        
    if not rec.event_id or int(rec.event_id) < 1:
        valid_data = False
        flash("You must select an event for this job")
    else:
        event_rec = Event(g.db).get(rec.event_id)
        if not event_rec:
            valid_data = False
            flash("That does not seem to be a valid Event ID")
            
    job_date = getDatetimeFromString(request.form.get("job_date",""))
    if not job_date:
        valid_data = False
        flash("That is not a valid date")
    #coerce the start and end datetimes
    #Get the start time into 24 hour format
    tempDatetime =coerce_datetime(request.form.get("job_date",""),request.form.get('start_time',''),request.form['start_time_AMPM'])
    if not tempDatetime:
        valid_data = False
        flash("That Date and Start Time are not valid")
    else:
        rec.start_date = tempDatetime
            
    tempDatetime =coerce_datetime(request.form.get("job_date",""),request.form.get('end_time',''),request.form['end_time_AMPM'])
    if not tempDatetime:
        valid_data = False
        flash("That Date and End Time are not valid")
    else:
        rec.end_date = tempDatetime
        

    if rec.start_date and rec.end_date and rec.start_date > rec.end_date:
        valid_data = False
        flash("The End Time can't be before the Start Time")
        
        
    # skill_list will be a string formatted like ":1:4:16:" so that a statement like
    #    'if ":16:" in skill_list' will return True.
    rec.skill_list = pack_list_to_string(skills_to_list()) #every element is wrapped in colons
    
    if not rec.skill_list:
        valid_data = False
        flash("You must select at least one Skill for the job.")

    return valid_data
    
    
def coerce_datetime(date_str,time_str,ampm=None):
    """Convert a string date and a string time into a datetime object
    if ampm is None, assume 24 hour time else 12 hour"""
    #import pdb;pdb.set_trace()
    
    tempDatetime = None
    time_parts = time_str.split(":")
    if len(time_parts) == 0 or time_parts[0] == '':
        valid_data = False
        flash("That is not a valid time")
    else:
        for key in range(len(time_parts)):
            if len(time_parts[key]) == 1:
                time_parts[key] = "0" + time_parts[key]
                    
        time_parts.extend(["00","00"])
        if ampm != None:
            if ampm.upper() == 'PM' and int(time_parts[0])<12:
                time_parts[0] = str(int(time_parts[0]) + 12)            
            if ampm.upper() == 'AM' and int(time_parts[0])> 12:
                time_parts[0] = str(int(time_parts[0]) - 12)            
        time_str = ":".join(time_parts[:3])
        tempDatetime = getDatetimeFromString("{} {}".format(date_str,time_str))
        
    return tempDatetime
    
def skills_to_list():
    """Create a list of skill (role) ids from form"""
    skills = []
    for role_id in request.form.getlist('skills'):
        skills.append(str(role_id))
    if not skills:
        # This is a hack that has to do with the way I submit the form via js
        # The 'skills' elements in request.form have the name 'skills[]' only when submitted
        #   via common.js.submitModalForm. Don't want to change it because it works elsewhere.
        # This may be an artifact of the way php handles multiple select elements
        for role_id in request.form.getlist('skills[]'):
            skills.append(str(role_id))
        
    
    return skills
    