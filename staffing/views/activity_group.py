from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import ActivityGroup

mod = Blueprint('activity_group',__name__, template_folder='templates/activity_group', url_prefix='/activitygroup')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Activity Groups'


@mod.route('/')
@table_access_required(ActivityGroup)
def display():
    setExits()
    g.title="Activity Group List"
    recs = ActivityGroup(g.db).select()
    
    return render_template('activity_group_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(ActivityGroup)
def edit(id=0):
    setExits()
    g.title = 'Edit Activity Group Record'
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    activity_group = ActivityGroup(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = activity_group.get(id)
        if not rec:
            flash("{} Record Not Found".format(activity_group.display_name))
            return redirect(g.listURL)
    else:
        rec = activity_group.new()
    
    if request.form:
        activity_group.update(rec,request.form)
        if valid_input(rec):
            activity_group.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
        
    return render_template('activity_group_edit.html',rec=rec)
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(ActivityGroup)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    activity_group = ActivityGroup(g.db)
    if id <= 0:
        return abort(404)
        
    if id > 0:
        rec = activity_group.get(id)
        
    if rec:
        activity_group.delete(rec.id)
        g.db.commit()
        flash("{} Activity Group Deleted".format(rec.name))
    
    return redirect(g.listURL)
    
    
def valid_input(rec):
    valid_data = True
    
    title = request.form.get('name').strip()
    if not title:
        valid_data = False
        flash("You must give the activity group a name")

    return valid_data