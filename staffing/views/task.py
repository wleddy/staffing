from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import Activity, Task

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
    g.title="Task List"
    recs = Task(g.db).select()
    
    return render_template('task_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(Task)
def edit(id=0):
    setExits()
    g.title = 'Edit Task Record'
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    task = Task(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = task.get(id)
        if not rec:
            flash("{} Record Not Found".format(task.name))
            return redirect(g.listURL)
    else:
        rec = task.new()
    
    if request.form:
        task.update(rec,request.form)
        if valid_input(rec):
            task.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
    activities = Activity(g.db).select()
            
    return render_template('task_edit.html',rec=rec,activities=activities)
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(Task)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    task = Task(g.db)
    if id <= 0:
        return abort(404)
        
    if id > 0:
        rec = task.get(id)
        
    if rec:
        task.delete(rec.id)
        g.db.commit()
        flash("{} Task Deleted".format(rec.name))
    
    return redirect(g.listURL)
    
    
def valid_input(rec):
    valid_data = True
    
    name = request.form.get('name').strip()
    if not name:
        valid_data = False
        flash("You must give the Task a name")
    if cleanRecordID(request.form.get('activity_id')) < 1 :
        valid_data = False
        flash("You must select an Activity")
        
    return valid_data