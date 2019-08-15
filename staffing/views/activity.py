from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import Activity, Event, ActivityType
from staffing.views.event import edit as edit_event, edit_from_activity as edit_event_from_activity

mod = Blueprint('activity',__name__, template_folder='templates/activity', url_prefix='/activity')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Activities'


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
    #import pdb;pdb.set_trace()
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    activity = Activity(g.db)
    #import pdb;pdb.set_trace()
    
    event_recs=None
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = activity.get(id)
        if not rec:
            flash("Record Not Found")
            return redirect(g.listURL)
    else:
        rec = activity.new()
        rec.title = "New Activity"
        activity.save(rec)
        g.cancelURL = url_for('.delete') + str(rec.id)
        g.db.commit()
    
    if request.form and save_activity():
        return redirect(g.listURL)
        
    activity_types = ActivityType(g.db).select()
    
    event_list = get_event_list(id)
            
    return render_template('activity_edit.html',
        rec=rec,
        activity_types=activity_types,
        event_list=event_list,
        )
    
    
def save_activity():
    activity = Activity(g.db)
    rec = activity.get(request.form.get('id',-1))
    if rec:
        activity.update(rec,request.form)
        if valid_input(rec):
            activity.save(rec)
            g.db.commit()
            return True
        
    return False
    
    
@mod.route('/edit_event/',methods=['POST',])
@mod.route('/edit_event/<int:event_id>/',methods=['POST',])
@table_access_required(Activity)
def edit_event(event_id=0):
    """Save the current record before switching to the event form
    Return the url of the page to be displayed
    """
    if not request.form:
        return abort(404)
        
    if save_activity():
        return url_for('event.edit_from_activity')+str(cleanRecordID(event_id))+"/"+request.form.get('id','-1')+"/"
    
    flash("Unable to save Activity changes")
    return url_for('activity.edit') + request.form.get('id','-1')+"/"


@mod.route('/get_event_list/',methods=['GET','POST',])
@mod.route('/get_event_list/<int:id>/',methods=['GET','POST',])
@table_access_required(Activity)
def get_event_list(id=0):
    """Return a fully formatted list of events for the activity specified"""
    #import pdb;pdb.set_trace()
    id = cleanRecordID(id)
    
    event_list = ''
    
    if id > 0:
        event_recs = get_event_recs(id)
        if event_recs:
            event_list = render_template("activity_event_list.html",event_recs=event_recs)
        
    return event_list
    
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
        flash("Activity {} Deleted".format(rec.title))
    
    return redirect(g.listURL)
    
    
def get_event_recs(activity_id=None,**kwargs):
    """Return a list of event records or None
     if 'event_id' is in kwargs, search for a single event, else 
     search for all events associated with activity_id.
     
    
    """
    
    activity_id = activity_id if activity_id else 0
    where = "event.activity_id = {}".format(activity_id)
    
    event_id = kwargs.get('event_id')
    if event_id:
        where = "event.id = {}".format(event_id)
        
    sql="""select event.id as event_id, 
    event.status,
    event.activity_id,
    coalesce(nullif(event.calendar_title,''),activity.title) as calendar_title,
    (select min(job.start_date) from job where job.event_id = event.id) as job_start_date,
    (select max(job.end_date) from job where job.event_id = event.id) as job_end_date,

    event.event_start_date,
    event.event_end_date,
    event.event_start_date_label_id,
    coalesce((select label from event_date_label where id = event.event_start_date_label_id ),'Event Start') as event_start_label,
    event.event_end_date_label_id,
    coalesce((select label from event_date_label where id = event.event_end_date_label_id ),'Event End') as event_end_label,
    event.service_start_date,
    event.service_end_date,
    event.service_start_date_label_id,
    coalesce((select label from event_date_label where id = event.service_start_date_label_id ),'Service Start') as service_start_label,
    event.service_end_date_label_id,
    coalesce((select label from event_date_label where id = event.service_end_date_label_id ),'Service End') as service_end_label,

    -- the number of positions filled in this event
    (select coalesce(sum(user_job.positions),0) from user_job
        where user_job.job_id in (select id from job where job.event_id = event.id)) as event_filled_positions,
    -- the total positions for this event
    (select coalesce(sum(job.max_positions),0) from job where job.event_id = event.id) as event_max_positions,
    coalesce(job.location_id,event.location_id) as event_location_id,
    location.location_name,
    location.lat,
    location.lng,
    location.street_address,
    location.city,
    location.state,
    location.zip,
    coalesce(nullif(event.service_type,''),(select type from activity_type where activity_type.id = activity.activity_type_id ),"Activity Type") as service_type,
    coalesce(nullif(event.description,''),activity.description) as event_description,
    coalesce(
        (select 1 from event where date(event.event_start_date,'localtime') < date('now','localtime') and event.id = job.event_id)
     ,0) 
    as is_past_event
    
    from event
    join activity on activity.id = event.activity_id
    left join job on event.id = job.event_id
    left join location on event_location_id = location.id
    where {where}
    group by event.event_start_date, event.location_id, job_start_date
    order by event.event_start_date DESC
    """.format(where=where)
    event_recs = Event(g.db).query(sql)
    
    return event_recs
    
    
def valid_input(rec):
    valid_data = True
    
    title = request.form.get('title').strip()
    if not title:
        valid_data = False
        flash("You must give the activity a name")

    return valid_data