from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.shotglass import get_app_config
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import Event, Location, EventType
from shotglass2.users.models import User
from staffing.views.job import get_job_list_for_event

mod = Blueprint('event',__name__, template_folder='templates/event', url_prefix='/event')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Events'


@mod.route('/')
@table_access_required(Event)
def display():
    setExits()
    g.title="Event List"
    recs = Event(g.db).select()
    
    return render_template('event_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(Event)
def edit(id=0):
    setExits()
    g.title = 'Edit Event Record'
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    event = Event(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = event.get(id)
        if not rec:
            flash("Record Not Found")
            return redirect(g.listURL)
    else:
        rec = event.new()
        user = User(g.db).get(g.user)
        rec.manager_user_id = user.id
        rec.title = "New Event"
        event.save(rec)
        g.cancelURL = url_for('.delete') + str(rec.id)
        g.db.commit()

    locations = Location(g.db).select()
    event_types = EventType(g.db).select()
    # only users of sufficient rank can manage an event
    where = "user.id in (select user_id from user_role where role_id in (select role.id from role where rank >= {}))".format(get_app_config().get('MINIMUM_MANAGER_RANK',70))
    event_managers = User(g.db).select(where=where)
    job_embed_list = get_job_list_for_event(rec.id)
    
    if request.form:
        event.update(rec,request.form)
        rec.location_id = cleanRecordID(request.form.get('location_id',-1))
        if valid_input(rec):
            event.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
        
    return render_template('event_edit.html',rec=rec,locations=locations,event_types=event_types,event_managers=event_managers,job_embed_list=job_embed_list)
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(Event)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    event = Event(g.db)
    if id <= 0:
        return abort(404)
        
    if id > 0:
        rec = event.get(id)
        
    if rec:
        event.delete(rec.id)
        g.db.commit()
        flash("{} Event Deleted".format(rec.title))
    
    return redirect(g.listURL)
    
    
def valid_input(rec):
    valid_data = True
    
    title = request.form.get('title').strip()
    if not title:
        valid_data = False
        flash("You must give the event a title")

    return valid_data