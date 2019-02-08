from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import EventType

mod = Blueprint('event_type',__name__, template_folder='templates/event_type', url_prefix='/eventtype')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Event Types'


@mod.route('/')
@table_access_required(EventType)
def display():
    setExits()
    g.title="Event Type List"
    recs = EventType(g.db).select()
    
    return render_template('event_type_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(EventType)
def edit(id=0):
    setExits()
    g.title = 'Edit Event Type Record'
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    event_type = EventType(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = event_type.get(id)
        if not rec:
            flash("{} Record Not Found".format(event_type.display_name))
            return redirect(g.listURL)
    else:
        rec = event_type.new()
    
    if request.form:
        event_type.update(rec,request.form)
        if valid_input(rec):
            event_type.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
        
    return render_template('event_type_edit.html',rec=rec)
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(EventType)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    event_type = EventType(g.db)
    if id <= 0:
        return abort(404)
        
    if id > 0:
        rec = event_type.get(id)
        
    if rec:
        event_type.delete(rec.id)
        g.db.commit()
        flash("{} Event Type Deleted".format(rec.type))
    
    return redirect(g.listURL)
    
    
def valid_input(rec):
    valid_data = True
    
    title = request.form.get('type').strip()
    if not title:
        valid_data = False
        flash("You must give the event type a name")

    return valid_data