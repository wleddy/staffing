from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.users.models import Role
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString
from staffing.models import Activity, Location, Task, UserTask
from staffing.utils import pack_list_to_string, un_pack_string

mod = Blueprint('task',__name__, template_folder='templates/task', url_prefix='/task')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Tasks'


@mod.route('/')
@table_access_required(Task)
def display():
    setExits()
    g.title="Activity Task List"
    recs = Task(g.db).select()
    
    return render_template('task_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/<int:activity_id>/',methods=['GET','POST',])
@table_access_required(Task)
def edit(id=0,activity_id=0,edit_from_list=False):
    setExits()
    g.title = 'Edit Task Record'
    #import pdb;pdb.set_trace()
    
    task_date=None
    start_time=None
    start_time_AMPM=None
    end_time=None
    end_time_AMPM=None
    
    if id == 0 and request.form:
        id = request.form.get('id',0)
        activity_id = request.form.get('activity_id',0)
    
    id = cleanRecordID(id)
    activity_id = cleanRecordID(activity_id)
    task = Task(g.db)
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = task.get(id)
        if not rec:
            flash("{} Record Not Found".format(task.display_name))
            return redirect(g.listURL)
        activity_id = rec.activity_id
    else:
        rec = task.new()
        rec.activity_id = activity_id
    
    current_activity = Activity(g.db).get(activity_id)
    activities = None
    if not current_activity:
        activities =  Activity(g.db).select() # This should only return current or future activities
    
    #import pdb;pdb.set_trace()
    
    roles = Role(g.db).select()
    selected_roles = [] # this needs to be populated from TaskRoles
        
    
    if request.form:
        task.update(rec,request.form)
        #rec.activity_id = cleanRecordID(request.form.get("activity_id"))
        if valid_input(rec):
            task.save(rec)
            g.db.commit()
            if edit_from_list:
                return 'success'
            return redirect(g.listURL)
        else:
            task_date=request.form.get('task_date',"")
            start_time=request.form.get('start_time',"")
            start_time_AMPM=request.form.get('start_time_AMPM',"AM")
            end_time=request.form.get('end_time',"")
            end_time_AMPM=request.form.get('end_time_AMPM',"AM")
    else:
        if rec.start_date and isinstance(rec.start_date,str):
            rec.start_date = getDatetimeFromString(rec.start_date)
        if rec.start_date:
            task_date=date_to_string(rec.start_date,'date')
            start_time=date_to_string(rec.start_date,'time')
            start_time_AMPM=date_to_string(rec.start_date,'ampm').upper()
        if rec.end_date and isinstance(rec.end_date,str):
            rec.start_date = getDatetimeFromString(rec.end_date)
        if rec.end_date:
            end_time=date_to_string(rec.end_date,'time')
            end_time_AMPM=date_to_string(rec.end_date,'ampm').upper()
            
    template = 'task_edit.html'
    if edit_from_list:
        template = 'task_embed_edit.html'
    
    return render_template(template,rec=rec,
            roles=roles,
            task_date=task_date,
            start_time=start_time,
            start_time_AMPM= start_time_AMPM,
            end_time=end_time,
            end_time_AMPM=end_time_AMPM,
            activities=activities,
            current_activity=current_activity,
            )
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(Task)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    task = Task(g.db)
    if id <= 0:
        return abort(404)
        
    rec = task.get(id)
        
    if rec:
        task.delete(rec.id)
        g.db.commit()
        flash("Task {} Deleted from {}".format(rec.title,task.display_name))
    
    return redirect(g.listURL)
    
    
@mod.route('/edit_from_list/<int:id>/',methods=['GET','POST',])
@mod.route('/edit_from_list/<int:id>',methods=['GET','POST',])
@mod.route('/edit_from_list/<int:id>/<int:activity_id>/',methods=['GET','POST',])
@mod.route('/edit_from_list/<int:id>/<int:activity_id>',methods=['GET','POST',])
@mod.route('/edit_from_list/',methods=['GET','POST',])
def edit_from_list(id=0,activity_id=0):
    return edit(id,activity_id,True)
    
    
@mod.route('/get_task_for_activity/',methods=['GET','POST',])
@mod.route('/get_task_for_activity/<int:id>/',methods=['GET','POST',])
def get_task_list_for_activity(id=0):
    """Return a fully formated html table for use in the Activity edit form"""
    id = cleanRecordID(id)
    tasks = Task(g.db).select(where='activity_id = {}'.format(id))
    return render_template('task_embed_list.html',tasks=tasks,activity_id=id)
    
    
def valid_input(rec):
    valid_data = True
    #import pdb;pdb.set_trace()
    
    task_title = request.form.get('title','').strip()
    if not task_title:
        valid_data = False
        flash("You must give the task a title")
        
    if not rec.activity_id or int(rec.activity_id) < 1:
        valid_data = False
        flash("You must select an activity for this task")
    else:
        activity_rec = Activity(g.db).get(rec.activity_id)
        if not activity_rec:
            valid_data = False
            flash("That does not seem to be a valid Activity ID")
            
    task_date = getDatetimeFromString(request.form.get("task_date",""))
    if not task_date:
        valid_data = False
        flash("That is not a valid date")
    #coerce the start and end datetimes
    #Get the start time into 24 hour format
    tempDatetime =coerce_datetime(request.form.get("task_date",""),request.form.get('start_time',''),request.form['start_time_AMPM'])
    if not tempDatetime:
        valid_data = False
        flash("That Date and Start Time are not valid")
    else:
        rec.start_date = tempDatetime
            
    tempDatetime =coerce_datetime(request.form.get("task_date",""),request.form.get('end_time',''),request.form['end_time_AMPM'])
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
        flash("You must select at least one Skill for the task.")

    return valid_data
    
    
def coerce_datetime(date_str,time_str,ampm):
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
            if ampm.upper() == 'PM' and int(time_parts[0])<13:
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
    