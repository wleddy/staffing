from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.mapping.views.maps import simple_map
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import Event, Location, Job, UserJob

mod = Blueprint('location',__name__, template_folder='templates/location', url_prefix='/location')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.display') + 'delete/'
    g.title = 'Locations'


# @mod.route('/')
# @table_access_required(Location)
# def display():
#     setExits()
#     g.title="Location List"
#     recs = Location(g.db).select()
#
#     return render_template('location_list.html',recs=recs)
    
    
from shotglass2.takeabeltof.views import TableView
PRIMARY_TABLE = Location
# this handles table list and record delete
@mod.route('/<path:path>',methods=['GET','POST',])
@mod.route('/<path:path>/',methods=['GET','POST',])
@mod.route('/',methods=['GET','POST',])
@table_access_required(PRIMARY_TABLE)
def display(path=None):
    # import pdb;pdb.set_trace()
    setExits()

    view = TableView(PRIMARY_TABLE,g.db)
    # optionally specify the list fields
    view.list_fields = [
            {'name':'id','label':'ID','class':'w3-hide-small','search':True},
            {'name':'location_name','label':'Location Name'},
            {'name':'street_address','label':'Address'},
            {'name':'city'},
        ]

    return view.dispatch_request()
  
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(Location)
def edit(id=0):
    setExits()
    g.title = 'Edit Location Record'
    map_html = None
    map_data = None
    search_field_id = None
    location = Location(g.db)
        
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
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
        rec.location_name = "New Location"
        search_field_id = 'search-input'
    
    if request.form:
        location.update(rec,request.form)
        if valid_input(rec):
            location.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
        
    
    #get the map for this
    # make a list of dict for the location
#     marker["dragable"] = point.get('dragable',False)
#     marker['map_icon'] = point.get('map_icon')
#     marker['lat'] = point.get('lat')
#     marker['lng'] = point.get('lng')
#     marker['UID'] = point.get('UID')
#     marker['title'] = point.get('title')
#     marker['location_name'] = point.get('location_name')
#     # for getting lat and lng values interactively from map
#     marker['latitudeFieldId'] = point.get('latitudeFieldId')
#     marker['longitudeFieldId'] = point.get('longitudeFieldId')
    if rec.lat and rec.lng:
        map_data = {'lat':rec.lat,'lng':rec.lng,
        'title':rec.location_name,
        'UID':rec.id,
        'draggable':True,
        'latitudeFieldId':'latitude',
        'longitudeFieldId':'longitude',
        }
    else:
        search_field_id = "search-input"
            
    map_html = simple_map(map_data,target_id='map',search_field_id=search_field_id)
        
    return render_template('location_edit.html',rec=rec,map_html=map_html,)
    
    
# @mod.route('/delete/',methods=['GET','POST',])
# @mod.route('/delete/<int:id>/',methods=['GET','POST',])
# @table_access_required(Location)
# def delete(id=0):
#     setExits()
#     id = cleanRecordID(id)
#     location = Location(g.db)
#     if id <= 0:
#         return abort(404)
#
#     if id > 0:
#         rec = location.get(id)
#
#     if rec:
#         location.delete(rec.id)
#         g.db.commit()
#         flash("{} Location Deleted".format(rec.location_name))
#
#     return redirect(g.listURL)
#
    
def valid_input(rec):
    valid_data = True
    
    location_name = request.form.get('location_name').strip()
    if not location_name:
        valid_data = False
        flash("You must give the location a location_name")

    return valid_data