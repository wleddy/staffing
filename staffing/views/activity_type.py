from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import ActivityType

mod = Blueprint('activity_type',__name__, template_folder='templates/activity_type', url_prefix='/activitytype')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Activity Types'


@mod.route('/')
@table_access_required(ActivityType)
def display():
    setExits()
    g.title="ActivityType List"
    recs = ActivityType(g.db).select()
    
    return render_template('activity_type_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(ActivityType)
def edit(id=0):
    setExits()
    g.title = 'Edit Activity Type Record'
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    activity_type = ActivityType(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = activity_type.get(id)
        if not rec:
            flash("{} Record Not Found".format(activity_type.display_name))
            return redirect(g.listURL)
    else:
        rec = activity_type.new()
    
    if request.form:
        activity_type.update(rec,request.form)
        if valid_input(rec):
            activity_type.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
        
    return render_template('activity_type_edit.html',rec=rec)
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(ActivityType)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    activity_type = ActivityType(g.db)
    if id <= 0:
        return abort(404)
        
    if id > 0:
        rec = activity_type.get(id)
        
    if rec:
        activity_type.delete(rec.id)
        g.db.commit()
        flash("{} Activity Type Deleted".format(rec.type))
    
    return redirect(g.listURL)
    
    
def valid_input(rec):
    valid_data = True
    
    title = request.form.get('type').strip()
    if not title:
        valid_data = False
        flash("You must give the activity type a name")

    return valid_data