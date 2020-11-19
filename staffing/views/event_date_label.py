from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string
from staffing.models import EventDateLabel

mod = Blueprint('event_date_label',__name__, template_folder='templates/event_date_label', url_prefix='/datelable')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.display') + 'delete/'
    g.title = 'Event Date Labels'


from shotglass2.takeabeltof.views import TableView
PRIMARY_TABLE = EventDateLabel
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
            {'name':'label','label':'Event Label'},
        ]

    return view.dispatch_request()
  

# @mod.route('/')
# @table_access_required(EventDateLabel)
# def display():
#     setExits()
#     g.title="Event Date Labels List"
#     recs = EventDateLabel(g.db).select()
#
#     return render_template('event_date_label_list.html',recs=recs)
    
    
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(EventDateLabel)
def edit(id=0):
    setExits()
    g.title = 'Edit Event Date Label Record'
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    event_label = EventDateLabel(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = event_label.get(id)
        if not rec:
            flash("Record Not Found")
            return redirect(g.listURL)
    else:
        rec = event_label.new()
    
    if request.form:
        event_label.update(rec,request.form)
        if valid_input(rec):
            event_label.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
        
    return render_template('event_date_label_edit.html',rec=rec)
    
    
@mod.route('/delete/',methods=['GET','POST',])
@mod.route('/delete/<int:id>/',methods=['GET','POST',])
@table_access_required(EventDateLabel)
def delete(id=0):
    setExits()
    id = cleanRecordID(id)
    event_label = EventDateLabel(g.db)
    if id <= 0:
        return abort(404)
        
    if id > 0:
        rec = event_label.get(id)
        
    if rec:
        event_label.delete(rec.id)
        g.db.commit()
        flash("Event Date Label '{}' Deleted".format(rec.label))
    
    return redirect(g.listURL)
    
    
def valid_input(rec):
    valid_data = True
    
    title = request.form.get('label').strip()
    if not title:
        valid_data = False
        flash("You must give the label a name")
        
    test_recs = EventDateLabel(g.db).select(where='lower(label) = lower("{}")'.format(request.form.get('label','Event Opens').strip()))
    if test_recs:
        for test in test_recs:
            if test.id != rec.id:
                valid_data = False
                flash("That label name is already in use.")
                break

    return valid_data