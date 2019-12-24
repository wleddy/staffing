from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
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
    g.deleteURL = url_for('.delete')
    g.title = 'Attendance'

@table_access_required(Attendance)
@mod.route('/',methods=['GET','POST'])
def display():
    setExits()
    g.title = 'Attendance List'
    
    sql = attendance_sql()
    #print(sql)
    recs = Attendance(g.db).query(sql)
    
    return render_template('attendance_list.html',recs=recs)

@mod.route('/edit/<int:att_id>',methods=['GET','POST'])
@mod.route('/edit/<int:att_id>/',methods=['GET','POST'])
@mod.route('/edit',methods=['GET','POST'])
@mod.route('/edit/',methods=['GET','POST'])
@login_required
def edit(att_id=0):
    """this is where users (staff) will record their work hours and other info"""
    setExits()
    g.title = 'Record Attendance'
        
    rec = None
    shift_hours = 0
    users = None
    tasks = Task(g.db).select()
    
    #import pdb;pdb.set_trace()
    att_id = cleanRecordID(request.form.get('id',att_id))
    if att_id < 0:
        flash("That is not a valid record id")
        return abort(404)
    if att_id == 0:
        rec = Attendance(g.db).new()
        rec.start_date = rec.end_date = date_to_string(local_datetime_now(),'iso_datetime')
        users = User(g.db).select()
    else:       
        sql = attendance_sql(where = "attendance.id = {}".format(att_id))
        rec = Attendance(g.db).query_one(sql)
    
        if not rec:
            flash('Could not access Attendance Record')
            return abort(404)
        
    #import pdb;pdb.set_trace()

    if not rec.start_date and rec.job_start_date:
        rec.start_date = rec.job_start_date
    if not rec.end_date and rec.job_end_date:
        rec.end_date = rec.job_end_date
        
    # If the current user is not the user_id requested or current user is not admin
    is_admin = g.admin.has_access(g.user,Attendance)
    if not is_admin and session.get('user_id') != rec.user_id:
        flash('You do not have access to this action')
        abort(404)
        
    if request.form:
        # Validate the Form
        if cleanRecordID(rec.id) > 0:
            # get a single table version of the record just so I can use .update()
            fresh_rec = Attendance(g.db).get(att_id)
        else:
            fresh_rec = rec #already a single table record
            
        Attendance(g.db).update(fresh_rec,request.form)
        fresh_rec.no_show = request.form.get('no_show','0')
        #import pdb;pdb.set_trace()
            
        if valid_form(fresh_rec):
            #import pdb;pdb.set_trace()
            # 12/23/19 - BL update the input_date and input_by fields
            if not fresh_rec.input_date:
                fresh_rec.input_date = local_datetime_now()
            if 'user_name' in session:
                fresh_rec.input_by = session['user_name']
                
            Attendance(g.db).save(fresh_rec)
            g.db.commit()
        
            return redirect(g.listURL)
            
        else:
            #import pdb;pdb.set_trace()
            # get any attendance record with space for all the related fields
            if att_id > 0:
                where = "attendance.id = {}".format(att_id)
            else:
                where = "attendance.id > 0"  # effectively, all records

            rec = Attendance(g.db).query(attendance_sql(where=where))
            if rec:
                rec = rec[0] #single record
                if att_id == 0:
                    #clear the record
                    for item in range(len(rec)):
                        rec[item] = None
                    
            else:
                flash("Error while handling validation error. No Attendance records found.")
                return redirect(g.listURL)
                    
            Attendance(g.db).update(rec,request.form)
            rec.start_date = date_to_string(getDatetimeFromString(get_start_time_from_form()),'iso_datetime')
            rec.end_date = date_to_string(getDatetimeFromString(get_end_time_from_form()),'iso_datetime')
            if not rec.end_date:
                rec.end_date = rec.start_date
                
            if rec.task_user_id:
                user = User(g.db).get(cleanRecordID(rec.task_user_id))
                if user:
                    rec.first_name = user.first_name
                    rec.last_name = user.last_name
                    
    shift_hours = int(request.form.get('shift_hours',0))
    
    if not shift_hours > 0 and rec.start_date and rec.end_date:
        shift_hours = (getDatetimeFromString(rec.end_date)- getDatetimeFromString(rec.start_date)).seconds / 3600
        
    # display the form
    return render_template('attendance_edit.html',
            rec=rec,
            no_delete=True,
            is_admin=is_admin,
            shift_hours=shift_hours,
            users=users,
            tasks=tasks,
            )
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET',])
@table_access_required(Attendance)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    attendance = Attendance(g.db)
    if id <= 0:
        return abort(404)
    
    if id > 0:
        rec = attendance.get(id)
    
    if rec:
        attendance.delete(rec.id)
        g.db.commit()
        flash("Attendance Record Deleted")

    return redirect(g.listURL)


def valid_form(rec):
    valid_form = True
    #import pdb;pdb.set_trace()
    
    task_id = request.form.get('task_id')
    if task_id != None:
        if Task(g.db).get(cleanRecordID(task_id)) == None:
            valid_form = False
            flash("You must select a task")
            
        # task user id must also be present
        if not User(g.db).get(cleanRecordID(request.form.get('task_user_id'))):
            valid_form = False
            flash("You must select a user")
    else:
        job_rec = UserJob(g.db).get(rec.user_job_id)
        if not job_rec:
            flash("Could not locate Job record")
            valid_form = False
        
    if valid_form and cleanRecordID(rec.no_show) == 1:
        #no reason to record anything else
        rec.start_date = None
        rec.end_date = None
        return True #short cut the function
    
    start_time = None
    end_time = None
    shift_hours = request.form.get('shift_hours')
    if shift_hours != None:
        # shift hours must be a number
        try:
            shift_hours = float(shift_hours)
            if shift_hours > 0:
                shift_hours = round(shift_hours,2)
                start_date = request.form.get('start_date_for_hours','')
                start_time = request.form.get('start_time_for_hours','')
                if start_date and start_time:
                    start_time = '{} {}'.format(start_date,start_time).strip()
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
        start_time = getDatetimeFromString(get_start_time_from_form())
        if not start_time:
            flash("That is not a valid Start time")
            valid_form = False
        
        end_time = getDatetimeFromString(get_end_time_from_form())
    
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
    """Record the selected attendance input form tab in the user session"""

    tab_clicked = request.form.get('tab_clicked')
    if tab_clicked:
        session['attendance_tab_select'] = tab_clicked
        
    return ''
    
@mod.route('/report',methods=['POST'])
@mod.route('/report/',methods=['POST'])
@table_access_required(Attendance)
def report():
    """Export the current selection of records as csv text"""
    
    setExits()
    selected_recs = request.form.get('selected_recs','')
    filename = "attendance_report_{}.csv".format(date_to_string(local_datetime_now(),'iso_datetime')).replace(' ','_')
    if selected_recs:
        # get attendance recs with this id
        recs = Attendance(g.db).query(attendance_sql(where="attendance.id in ({})".format(selected_recs)))
        if recs:
            result = render_template("attendance_report.csv", recs=recs)
            headers={
               "Content-Disposition":"attachment;filename={}".format(filename),
                }

            return Response(
                    result,
                    mimetype="text/csv",
                    headers=headers
                    )
            
    flash("No records to report")
    return redirect(g.listURL)
    
def attendance_sql(**kwargs):
    """Return the sql statement to use to in input and edit forms"""
    
    # defaults are for list selection
    #where = kwargs.get('where',"date(job_start_date, 'localtime') <= date('now','localtime') and is_volunteer_job = 0")
    where = kwargs.get('where'," is_volunteer_job = 0")
    order_by = kwargs.get('order_by',"date(job_start_date,'localtime') DESC , activity_title, job_title, first_name, last_name")
    
    sql = """select
    attendance.*,
    coalesce(job.start_date,attendance.start_date) as job_start_date,
    coalesce(job.end_date,attendance.end_date) as job_end_date,
    coalesce(activity.title,task_activity.title,'No Task Title') as activity_title, 
    coalesce(user.first_name,task_user.first_name) as first_name,
    coalesce(user.last_name,task_user.last_name) as last_name,
    coalesce(nullif(event.calendar_title,''),activity.title,task_activity.title,'No Activity Title') as calendar_title,
    coalesce(job.title,task.name) as job_title, 
    
    -- 1 if a volunteer job, else 0
    coalesce((select 1 from job_role where job_role.role_id in ({vol_role_ids}) and job_role.job_id = job.id),0) as is_volunteer_job
    from attendance
    left join user_job on user_job.id = attendance.user_job_id
    left join job on user_job.job_id = job.id
    left join user on user.id = user_job.user_id
    left join user as task_user on task_user.id = attendance.task_user_id
    left join task on task.id = attendance.task_id
    left join event on event.id = job.event_id
    left join activity as task_activity on task_activity.id = task.activity_id
    left join activity on activity.id = event.activity_id
    
    where {where}
    order by {order_by}
    """.format(vol_role_ids=get_volunteer_role_ids(),where=where,order_by=order_by)
    
    return sql
    
    
def get_start_time_from_form():
    """Return a start time using form data else the empty string"""
    return '{} {}'.format(request.form.get('att_start_date',request.form.get('start_date_for_hours','')),request.form.get('att_start_time',request.form.get('start_time_for_hours',''))).strip()
    
def get_end_time_from_form():
    """Return a end time using form data else the empty string"""
    return '{} {}'.format(request.form.get('att_end_date',request.form.get('end_date_for_hours','')),request.form.get('att_end_time',request.form.get('end_time_for_hours',''))).strip()
