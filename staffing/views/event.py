from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.shotglass import get_site_config
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString
from staffing.models import Event, Location, EventType, Client, EventDateLabel
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
    
    
@mod.route('/edit/',methods=['POST',])
@mod.route('/edit/<int:id>/<int:activity_id>',methods=['GET','POST',])
@mod.route('/edit/<int:id>/<int:activity_id>/',methods=['GET','POST',])
@table_access_required(Event)
def edit(id=0,activity_id=None):
    setExits()
    g.title = 'Edit Event Record'
    if cleanRecordID(id) == 0:
        g.cancelURL = g.deleteURL
        
    return render_edit_form(id,activity_id)
    
    
@mod.route('/edit_from_activity/',methods=['POST',])
@mod.route('/edit_from_activity/<int:id>/<int:activity_id>',methods=['GET','POST',])
@mod.route('/edit_from_activity/<int:id>/<int:activity_id>/',methods=['GET','POST',])
@table_access_required(Event)
def edit_from_activity(id=0,activity_id=-1):
    """Create or edit an Event record from the Activity input form"""
    #import pdb;pdb.set_trace()
    setExits()
    g.title = 'Edit Event Record'
    
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        activity_id = cleanRecordID(request.form.get("activity_id"))
        
    # Return to Activty record when done with edit
    g.editURL = url_for('event.edit_from_activity')
    g.listURL = url_for('activity.edit') + str(cleanRecordID(activity_id))
    g.deleteURL = url_for('event.delete_from_activity')+ str(cleanRecordID(activity_id)) + "/" 
    if cleanRecordID(id) == 0:
        g.cancelURL = g.deleteURL
        

    return render_edit_form(id,activity_id)
    
    
def render_edit_form(id,activity_id):
    #import pdb;pdb.set_trace()
    id = cleanRecordID(id)
    activity_id = cleanRecordID(activity_id)
        
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        activity_id = cleanRecordID(request.form.get("activity_id"))
        
    if activity_id == None and id == 0:
        #can't create a new record without an activity link
        return abort(404)
        
    event = Event(g.db)
    clients = Client(g.db).select()
    event_date_labels=EventDateLabel(g.db).select()
    
    if id < 0 or activity_id < 0:
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
        rec.activity_id = activity_id
        event.save(rec)
        g.db.commit()
        g.cancelURL = g.cancelURL + str(rec.id)
        # fetch the record again to load the related activity data
        rec = event.get(rec.id)

    if request.form:
        #import pdb;pdb.set_trace()
        event.update(rec,request.form)
        rec.exclude_from_calendar = request.form.get('exclude_from_calendar',0) #checkbox value
        rec.location_id = cleanRecordID(request.form.get('location_id',-1))
        # ensure that web address is absolute
        if rec.client_website:
            data_part = rec.client_website.partition("//")
            if data_part[0][:4] != 'http':
                rec.client_website = 'http://' + rec.client_website
            
        if valid_input(rec):
            event.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
    # get lists for form
    client = Client(g.db).get(rec.client_id)
    locations = Location(g.db).select()
    event_types = EventType(g.db).select()
    # only users of sufficient rank can manage an event
    where = "user.id in (select user_id from user_role where role_id in (select role.id from role where rank >= {}))".format(get_site_config().get('MINIMUM_MANAGER_RANK',70))
    event_managers = User(g.db).select(where=where)
    job_embed_list = get_job_list_for_event(rec.id)
       
        
    return render_template('event_edit.html',
        rec=rec,
        locations=locations,
        event_types=event_types,
        event_managers=event_managers,
        clients=clients,client=client,
        job_embed_list=job_embed_list,
        event_date_labels=event_date_labels,
        )
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(Event)
def delete(id=0):
    setExits()
    return handle_delete(id)
    
def handle_delete(id):
    id = cleanRecordID(id)
    event = Event(g.db)
    if id <= 0:
        return abort(404)
        
    if id > 0:
        rec = event.get(id)
        
    if rec:
        event.delete(rec.id)
        g.db.commit()
    
    return redirect(g.listURL)
    
@mod.route('/delete_from_activity/',methods=['GET','POST',])
@mod.route('/delete_from_activity/<int:activity_id>/<int:id>/',methods=['GET','POST',])
def delete_from_activity(activity_id=-1,id=0):
    """Delete a record, but then return to the activity record
    Watch out! the params are swapped from usual
    """
    g.listURL = url_for('activity.edit') + str(cleanRecordID(activity_id))
    return handle_delete(id)
    
def valid_input(rec):
    valid_data = True
    
    if not rec.exclude_from_calendar:
        # validate and convert start and end dates to timezone aware date strings
        form_datetime = request.form.get("event_start_date",'')
        if not form_datetime:
            valid_data = False
            flash("Enter a Start time for the event")
        else:
            temp_datetime = getDatetimeFromString(form_datetime)
            if temp_datetime == None:
                #Failed conversion
                valid_data = False
                flash("That is not a valid Start date")
            else:
                rec.event_start_date = temp_datetime #store as date time
            
        form_datetime = request.form.get("event_end_date",'')
        if not form_datetime:
            valid_data = False
            flash("Enter an end time for the event")
        else:
            temp_datetime = getDatetimeFromString(form_datetime)
            if temp_datetime == None:
                #Failed conversion
                valid_data = False
                flash("That is not a valid End date")
            else:
                rec.event_end_date = temp_datetime #store as date time

        form_datetime = request.form.get("service_start_date",'')
        if not form_datetime:
            valid_data = False
            flash("Enter a Start time for the service")
        else:
            temp_datetime = getDatetimeFromString(form_datetime)
            if temp_datetime == None:
                #Failed conversion
                valid_data = False
                flash("That is not a valid Start date")
            else:
                rec.service_start_date = temp_datetime #store as date time
            
        form_datetime = request.form.get("service_end_date",'')
        if not form_datetime:
            valid_data = False
            flash("Enter an end time for the service")
        else:
            temp_datetime = getDatetimeFromString(form_datetime)
            if temp_datetime == None:
                #Failed conversion
                valid_data = False
                flash("That is not a valid End date")
            else:
                rec.service_end_date = temp_datetime #store as date time
            
    return valid_data