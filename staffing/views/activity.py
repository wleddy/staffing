from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import Activity, Location, Spot, UserSpot
from shotglass2.users.models import User

mod = Blueprint('activity',__name__, template_folder='templates/activity', url_prefix='/activity')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Activitys'


@mod.route('/')
@table_access_required(Activity)
def display():
    setExits()
    g.title="Activity List"
    recs = Activity(g.db).select()
    
    return render_template('activity_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(Activity)
def edit(id=0):
    setExits()
    g.title = 'Edit Activity Record'
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    activity = Activity(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = activity.get(id)
        if not rec:
            flash("Record Not Found")
            return redirect(g.listURL)
    else:
        rec = activity.new()
        user = User(g.db).get(g.user)
        rec.manager_name = " ".join([user.first_name,user.last_name])
        rec.manager_email = user.email
        rec.manager_phone = user.phone

    locations = Location(g.db).select()
    
    if request.form:
        activity.update(rec,request.form)
        rec.location_id = cleanRecordID(request.form.get('location_id',-1))
        if valid_input(rec):
            activity.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
        
    return render_template('activity_edit.html',rec=rec,locations=locations)
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(Activity)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    activity = Activity(g.db)
    if id <= 0:
        return abort(404)
        
    if id > 0:
        rec = activity.get(id)
        
    if rec:
        activity.delete(rec.id)
        g.db.commit()
        flash("{} Activity Deleted".format(rec.title))
    
    return redirect(g.listURL)
    
    
def valid_input(rec):
    valid_data = True
    
    title = request.form.get('title').strip()
    if not title:
        valid_data = False
        flash("You must give the activity a title")

    return valid_data