from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import Event, Location, Spot, UserSpot

mod = Blueprint('location',__name__, template_folder='templates/location', url_prefix='/location')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Locations'


@mod.route('/')
@table_access_required(Location)
def display():
    setExits()
    g.title="Location List"
    recs = Location(g.db).select()
    
    return render_template('location_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(Location)
def edit(id=0):
    setExits()
    g.title = 'Edit Location Record'
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    location = Location(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = location.get(id)
        if not rec:
            flash("{} Record Not Found".format(location.display_name))
            return redirect(g.listURL)
    else:
        rec = location.new()

    locations = Location(g.db).select()
    
    if request.form:
        location.update(rec,request.form)
        if valid_input(rec):
            location.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
        
    return render_template('location_edit.html',rec=rec,locations=locations)
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(Location)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    location = Location(g.db)
    if id <= 0:
        return abort(404)
        
    if id > 0:
        rec = location.get(id)
        
    if rec:
        location.delete(rec.id)
        g.db.commit()
        flash("{} Location Deleted".format(rec.location_name))
    
    return redirect(g.listURL)
    
    
def valid_input(rec):
    valid_data = True
    
    location_name = request.form.get('location_name').strip()
    if not location_name:
        valid_data = False
        flash("You must give the location a location_name")

    return valid_data