from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.users.models import Role, User
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString, local_datetime_now
from shotglass2.shotglass import get_site_config
from staffing.models import Event, Location, Job, UserJob
from staffing.views.signup import get_job_rows

mod = Blueprint('attendance',__name__, template_folder='templates/attendance', url_prefix='/attendance')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
#     g.deleteURL = url_for('.delete')
    g.title = 'Attendance'

@table_access_required(UserJob)
@mod.route('/',methods=['GET','POST'])
def display():
    setExits()
    g.title = 'Attendance List'
    sql = """
    select
    user_job.*,
    
    job.start_date as job_start_date,
    job.end_date as job_end_date,

    event.id as event_id,
    activity.title as activity_title, 
    coalesce(nullif(event.calendar_title,''),activity.title) as calendar_title,
    job.title as job_title, 
    job.start_date as start_date,

    user.first_name,
    user.last_name

    from user_job
    join job on user_job.job_id = job.id
    join user on user_job.user_id = user.id
    join event on job.event_id = event.id
    join activity on activity.id = event.activity_id
    where date(start_date, 'localtime') < date('now','localtime')
    order by date(start_date,'localtime') DESC , activity_title, job_title, first_name, last_name
    """
    recs = UserJob(g.db).query(sql)
    
    return render_template('attendance_list.html',recs=recs)

@mod.route('/edit/<int:userjob_id>',methods=['GET','POST'])
@mod.route('/edit/<int:userjob_id>/',methods=['GET','POST'])
@mod.route('/edit',methods=['GET','POST'])
@mod.route('/edit/',methods=['GET','POST'])
@login_required
def edit(userjob_id=None):
    """this is where users (staff) will record their work hours and other info"""
    setExits()
    g.title = 'Edit Attendance'
        
    #import pdb;pdb.set_trace()
    userjob_id = cleanRecordID(request.form.get('id',userjob_id))
    rec = None
    if userjob_id < 0:
        flash("That is not a valid record id")
        return abort(404)
    if userjob_id == 0:
        rec = UserJob(g.db).new()
    else:
        sql = """
        select 
        user_job.*,
        
        event.id as event_id,
        activity.title as activity_title, 
        coalesce(nullif(event.calendar_title,''),activity.title) as calendar_title,
        job.title as job_title, 
        job.start_date as job_start_date,
        job.end_date as job_end_date,
        user.first_name,
        user.last_name

        from user_job
        join job on user_job.job_id = job.id
        join user on user_job.user_id = user.id
        join event on job.event_id = event.id
        join activity on activity.id = event.activity_id
        where user_job.id = {}
        order by user_job.id
        """.format(userjob_id)
        rec = UserJob(g.db).query_one(sql)
    
        if not rec:
            flash('Could not access Attendance Record')
            return abort(404)
        
    #import pdb;pdb.set_trace()
        
    # If the current user is not the user_id requested or current user is not admin
    is_admin = g.admin.has_access(g.user,UserJob)
    if not is_admin and session.get('user_id') != rec.user_id:
        flash('You do not have access to this action')
        abort(404)
        
    if request.form:
        # Validate the Form
        # get a single table version of the record
        fresh_rec = UserJob(g.db).get(userjob_id)
        UserJob(g.db).update(fresh_rec,request.form)
        
        #import pdb;pdb.set_trace()
            
        if valid_form(fresh_rec):
            # Save the updated record
            UserJob(g.db).save(fresh_rec)
            g.db.commit()
            # Go somewhere else
        
            return redirect(g.listURL)
            
        else:
            UserJob(g.db).update(rec,request.form)
            
        
    # display the form
    return render_template('attendance_edit.html',rec=rec,no_delete=True,is_admin=is_admin)
    
    
def valid_form(rec):
    is_valid = True
    #import pdb;pdb.set_trace()
    
    job_rec = Job(g.db).get(rec.job_id)
    if not job_rec:
        flash("Could not locate Job record")
        is_valid = False
        
    # start and end times must be present
    start_time = request.form.get('att_start_time','')
    start_date = request.form.get('att_start_date','')
    # Try to append this time onto the job start date
    start_time = '{} {}'.format(start_date,start_time)
    start_time = getDatetimeFromString(start_time) 
    
    if not start_time or type(start_time) == str:
        flash("That is not a valid Start time")
        is_valid = False
        
    end_time = request.form.get('att_end_time','')
    end_date = request.form.get('att_end_date','')
    # Try to append this time onto the job start date
    end_time = '{} {}'.format(end_date,end_time)
    end_time = getDatetimeFromString(end_time) 
    
    if not end_time or type(end_time) == str:
        flash("That is not a valid End time")
        is_valid = False
        
        
    if start_time and end_time:
        if start_time > end_time:
            flash("The Start time cannot be after the End Time")
            is_valid = False
        else:
            rec.attendance_start = start_time
            rec.attendance_end = end_time
        
        
    return is_valid