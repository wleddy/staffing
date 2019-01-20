from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.users.models import Role
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import date_to_string, getDatetimeFromString
from staffing.models import Event, Location, Spot, UserSpot

mod = Blueprint('spot',__name__, template_folder='templates/spot', url_prefix='/spot')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Spots'


@mod.route('/')
@table_access_required(Spot)
def display():
    setExits()
    g.title="Event Spot List"
    recs = Spot(g.db).select()
    
    return render_template('spot_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/<int:event_id>/',methods=['GET','POST',])
@table_access_required(Spot)
def edit(id=0,event_id=0):
    setExits()
    g.title = 'Edit Spot Record'
    id = cleanRecordID(id)
    event_id = cleanRecordID(event_id)
    current_event = None
    if event_id > 0:
        current_event = Event(g.db).get(event_id)
        
    events =  Event(g.db).select() # This should only return current or future events
    
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    spot = Spot(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = spot.get(id)
        if not rec:
            flash("{} Record Not Found".format(spot.display_name))
            return redirect(g.listURL)
    else:
        rec = spot.new()
        rec.event_id = event_id

    roles = Role(g.db).select()
    selected_roles = [] # this needs to be populated from SpotRoles
        
    
    if request.form:
        spot.update(rec,request.form)
        rec.event_id = cleanRecordID(request.form.get("event_id"))
        if valid_input(rec):
            skills = []
            if 'skills' in request.form:
                #delete all the users current roles
                for role_id in request.form.getlist('skills'):
                    skills.append(str(role_id))
                    
            # role_list will be a string formatted like ":1:4:16:" so that a statement like
            #    'if ":16:" in role_list' will return True.
            rec.role_list = ":" + ':'.join(skills) + ":" #every element is wrapped in colons
            spot.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        else:
            spot_date=request.form.get('spot_date',"")
            start_time=request.form.get('start_time',"")
            start_time_AMPM=request.form.get('start_time_AMPM',"AM")
            end_time=request.form.get('end_time',"")
            end_time_AMPM=request.form.get('end_time_AMPM',"AM")
        
    spot_date=None
    start_time=None
    start_time_AMPM=None
    end_time=None
    end_time_AMPM=None
    
    if rec.start_date and isinstance(rec.start_date,str):
        rec.start_date = getDatetimeFromString(rec.start_date)
    if rec.start_date:
        spot_date=date_to_string(rec.start_date,'date')
        start_time=date_to_string(rec.start_date,'time')
        start_time_AMPM=date_to_string(rec.start_date,'ampm').upper()
    if rec.end_date and isinstance(rec.end_date,str):
        rec.start_date = getDatetimeFromString(rec.end_date)
    if rec.end_date:
        end_time=date_to_string(rec.end_date,'time')
        end_time_AMPM=date_to_string(rec.end_date,'ampm').upper()
    
    return render_template('spot_edit.html',rec=rec,
            roles=roles,
            spot_date=spot_date,
            start_time=start_time,
            start_time_AMPM= start_time_AMPM,
            end_time=end_time,
            end_time_AMPM=end_time_AMPM,
            events=events,
            current_event=current_event,
            )
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(Spot)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    spot = Spot(g.db)
    if id <= 0:
        return abort(404)
        
    rec = spot.get(id)
        
    if rec:
        spot.delete(rec.id)
        g.db.commit()
        flash("{} Spot Deleted from {}".format(rec.name,spot.display_name))
    
    return redirect(g.listURL)
    
    
def valid_input(rec):
    valid_data = True
    #import pdb;pdb.set_trace()
    
    spot_name = request.form.get('title','').strip()
    if not spot_name:
        valid_data = False
        flash("You must give the spot a title")
        
    if not rec.event_id or rec.event_id < 1:
        valid_data = False
        flash("You must select an event for this spot")
    else:
        event_rec = Event(g.db).get(rec.event_id)
        if not event_rec:
            valid_data = False
            flash("That does not seem to be a valid Event ID")
            
    spot_date = getDatetimeFromString(request.form.get("spot_date",""))
    if not spot_date:
        valid_data = False
        flash("That is not a valid date")
    #coerse the start and end datetimes
    #Get the start time into 24 hour format
    tempDatetime =coerse_time(request.form.get("spot_date",""),request.form.get('start_time',''),request.form['start_time_AMPM'])
    if not tempDatetime:
        valid_data = False
        flash("That Date and Start Time are not valid")
    else:
        rec.start_date = tempDatetime
            
    tempDatetime =coerse_time(request.form.get("spot_date",""),request.form.get('end_time',''),request.form['end_time_AMPM'])
    if not tempDatetime:
        valid_data = False
        flash("That Date and End Time are not valid")
    else:
        rec.end_date = tempDatetime
        

    if rec.start_date and rec.end_date and rec.start_date > rec.end_date:
        valid_data = False
        flash("The End Time can't be before the Start Time")
        
        
    if not request.form.get('skills'):
        valid_data = False
        flash("You must select at least one Skill for the spot.")
        
    return valid_data
    
    
def coerse_time(date_str,time_str,ampm):
    #import pdb;pdb.set_trace()
    
    tempDatetime = None
    time_parts = time_str.split(":")
    if len(time_parts) == 0:
        valid_data = False
        flash("That is not a valid Start time")
    else:
        for key in range(len(time_parts)):
            if len(time_parts[key]) == 1:
                time_parts[key] = "0" + time_parts[key]
                    
        time_parts.extend(["00","00"])
        if ampm == 'PM' and int(time_parts[0])<13:
            time_parts[0] = str(int(time_parts[0]) + 12)            
        time_str = ":".join(time_parts[:3])
        tempDatetime = getDatetimeFromString("{} {}".format(date_str,time_str))
        
    return tempDatetime
    