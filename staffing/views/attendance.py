from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from datetime import timedelta
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.users.models import Role, User
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString, local_datetime_now
from shotglass2.shotglass import get_site_config
from staffing.models import Event, Location, Job, UserJob, Attendance, Task
from staffing.views.signup import get_job_rows, get_volunteer_role_ids

mod = Blueprint('attendance',__name__, template_folder='templates/attendance', url_prefix='/attendance')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
#     g.deleteURL = url_for('.delete')
    g.title = 'Attendance'

@table_access_required(Attendance)
@mod.route('/',methods=['GET','POST'])
def display():
    setExits()
    g.title = 'Attendance List'
    
    #get the ids for vounteer roles
    vol_role_ids = get_volunteer_role_ids()
        
    sql = """
    select
    attendance.*,
    
    job.start_date as job_start_date,
    job.end_date as job_end_date,

    event.id as event_id,
    activity.title as activity_title, 
    coalesce(nullif(event.calendar_title,''),activity.title) as calendar_title,
    job.title as job_title, 
    
    -- 1 if a volunteer job, else 0
    coalesce((select 1 from job_role where job_role.role_id in ({vol_role_ids}) and job_role.job_id = job.id),0) as is_volunteer_job,
    
    user.first_name,
    user.last_name

    from attendance
    join user_job on user_job.id = attendance.user_job_id
    join job on user_job.job_id = job.id
    join user on user_job.user_id = user.id
    join event on job.event_id = event.id
    join activity on activity.id = event.activity_id
    where date(job.start_date, 'localtime') < date('now','localtime') and is_volunteer_job = 0
    order by date(job.start_date,'localtime') DESC , activity_title, job_title, first_name, last_name
    """.format(vol_role_ids=vol_role_ids)
    recs = Attendance(g.db).query(sql)
    
    return render_template('attendance_list.html',recs=recs)

@mod.route('/edit/<int:att_id>',methods=['GET','POST'])
@mod.route('/edit/<int:att_id>/',methods=['GET','POST'])
@mod.route('/edit',methods=['GET','POST'])
@mod.route('/edit/',methods=['GET','POST'])
@login_required
def edit(att_id=None):
    """this is where users (staff) will record their work hours and other info"""
    setExits()
    g.title = 'Record Attendance'
        
    rec = None
    shift_hours = 0
    
    #import pdb;pdb.set_trace()
    att_id = cleanRecordID(request.form.get('id',att_id))
    if att_id < 0:
        flash("That is not a valid record id")
        return abort(404)
    if att_id == 0:
        rec = Attendance(g.db).new()
    else:
        sql = """
        select 
        attendance.*,
        
        event.id as event_id,
        activity.title as activity_title, 
        coalesce(nullif(event.calendar_title,''),activity.title) as calendar_title,
        job.title as job_title, 
        job.start_date as job_start_date,
        job.end_date as job_end_date,
        user.first_name,
        user.last_name

        from attendance
        join user_job on user_job.id = attendance.user_job_id
        join job on user_job.job_id = job.id
        join user on user_job.user_id = user.id
        join event on job.event_id = event.id
        join activity on activity.id = event.activity_id
        where attendance.id = {}
        order by attendance.id
        """.format(att_id)
        rec = Attendance(g.db).query_one(sql)
    
        if not rec:
            flash('Could not access Attendance Record')
            return abort(404)
        
    #import pdb;pdb.set_trace()

    if not rec.start_date and rec.job_start_date:
        rec.start_date = rec.job_start_date
    if not rec.end_date and rec.job_end_date:
        rec.end_date = rec.job_end_date
        
    if rec.start_date and rec.end_date:
        shift_hours = (getDatetimeFromString(rec.end_date) - getDatetimeFromString(rec.start_date)).seconds / 3600
        
    # If the current user is not the user_id requested or current user is not admin
    is_admin = g.admin.has_access(g.user,Attendance)
    if not is_admin and session.get('user_id') != rec.user_id:
        flash('You do not have access to this action')
        abort(404)
        
    if request.form:
        # Validate the Form
        # get a single table version of the record just so I can use .update()
        fresh_rec = Attendance(g.db).get(att_id)
        Attendance(g.db).update(fresh_rec,request.form)
        
        #import pdb;pdb.set_trace()
            
        if valid_form(fresh_rec):
            Attendance(g.db).save(fresh_rec)
            g.db.commit()
        
            return redirect(g.listURL)
            
        else:
            Attendance(g.db).update(rec,request.form)            
        
    # display the form
    return render_template('attendance_edit.html',rec=rec,no_delete=True,is_admin=is_admin,shift_hours=shift_hours)
    
    
def valid_form(rec):
    valid_form = True
    #import pdb;pdb.set_trace()
    
    job_rec = UserJob(g.db).get(rec.user_job_id)
    if not job_rec:
        flash("Could not locate Job record")
        valid_form = False
        
    if int(rec.no_show) == 1:
        #no reason to record anything else
        rec.start_date = None
        rec.end_date = None
        return True
    
    start_time = None
    end_time = None
    shift_hours = request.form.get('shift_hours')
    if shift_hours != None:
        # shift hours must be a number
        try:
            shift_hours = float(shift_hours)
            if shift_hours > 0:
                start_date = request.form.get('start_date_for_hours','')
                start_time = request.form.get('start_time_for_hours','')
                if start_date and start_time:
                    start_time = '{} {}'.format(start_date,start_time)
                    start_time = getDatetimeFromString(start_time) 
                    if start_time:
                        end_time = start_time + timedelta(seconds=shift_hours * 3600)
                    else:
                        valid_form = False
                        flash(printException("That is not a valid Start Date or time"))
                else:
                    valid_form = False
                    flash(printException("Start Date or time is missing."))
            else:
                valid_form = False
                flash("Hours Worked must be greater than 0")
        except:
            valid_form = False
            flash("Shift Hours must be a number.")
            
    else:
        # start and end times must be present
        start_time = request.form.get('att_start_time','')
        start_date = request.form.get('att_start_date','')
        # Try to append this time onto the job start date
        start_time = '{} {}'.format(start_date,start_time)
        start_time = getDatetimeFromString(start_time) 
    
        if not start_time:
            flash("That is not a valid Start time")
            valid_form = False
        
        end_time = request.form.get('att_end_time','')
        end_date = request.form.get('att_end_date','')
        # Try to append this time onto the job start date
        end_time = '{} {}'.format(end_date,end_time)
        end_time = getDatetimeFromString(end_time) 
    
        if not end_time:
            flash("That is not a valid End time")
            valid_form = False
        
        
    if start_time and end_time:
        if start_time > end_time:
            flash("The Start time cannot be after the End Time")
            valid_form = False
        else:
            rec.start_date = start_time
            rec.end_date = end_time
        
        
    return valid_form
    
    
@mod.route('/tab_select',methods=['POST'])
@mod.route('/tab_select/',methods=['POST'])
@login_required
def tab_select():
    """Record the select attenance input form tab in the user session"""

    tab_clicked = request.form.get('tab_clicked')
    if tab_clicked:
        session['attendance_tab_select'] = tab_clicked
        
    return ''