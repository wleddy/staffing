from datetime import datetime
from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.shotglass import get_site_config
from shotglass2.takeabeltof.utils import printException, cleanRecordID, looksLikeEmailAddress
from shotglass2.users.admin import login_required, table_access_required
from staffing.models import Client
from time import time


mod = Blueprint('client',__name__, template_folder='templates/client', url_prefix='/client')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.homeURL = '/'
    g.title = 'Client'

    
@mod.route('/', methods=['GET'])
@table_access_required(Client)
def display():
    setExits()
    g.title = "{} List".format(g.title)
    
    recs = Client(g.db).select()
    return render_template('client_list.html', recs=recs)
    
## Edit the client record
@mod.route('/edit/',methods=['GET','POST',])
@mod.route('/edit/<int:id>/',methods=['GET','POST',])
@table_access_required(Client)
def edit(id=0):
    setExits()
    g.title = 'Edit Activity Type Record'
    id = cleanRecordID(id)
    if request.form:
        id = cleanRecordID(request.form.get("id"))
        
    client = Client(g.db)
    #import pdb;pdb.set_trace()
    
    if id < 0:
        return abort(404)
        
    if id > 0:
        rec = client.get(id)
        if not rec:
            flash("{} Record Not Found".format(client.display_name))
            return redirect(g.listURL)
    else:
        rec = client.new()
    
    if request.form:
        client.update(rec,request.form)
        if valid_input(rec):
            client.save(rec)
            g.db.commit()
            return redirect(g.listURL)
        
        
    return render_template('client_edit.html',rec=rec)
            
        
@mod.route('/delete', methods=['GET'])
@mod.route('/delete/', methods=['GET'])
@mod.route('/delete/<int:rec_id>/', methods=['GET'])
@table_access_required(Client)
def delete(rec_id=None):
    setExits()
    delete_by_admin = request.args.get('delete',None)
    if delete_by_admin:
        client = Client(g.db)
        rec=client.select_one(where='access_token = "{}"'.format(delete_by_admin.strip()))
        if rec:
            rec_id = rec.id
    
    if rec_id == None:
        rec_id = request.form.get('id',request.args.get('id',-1))
    
    rec_id = cleanRecordID(rec_id)
    if rec_id <=0:
        flash("That is not a valid record ID")
        return redirect(g.listURL)
        
    rec = Client(g.db).get(rec_id,include_inactive=True)
    if not rec:
        flash("Record not found")
    else:
        Client(g.db).delete(rec.id)
        g.db.commit()
        flash('Client Record Deleted')
        
    return redirect(g.listURL)


def valid_input(rec):
    # Validate the form
    goodForm = True
    client = Client(g.db)
    
    if request.form['email'].strip() == '':
        goodForm = False
        flash('Email may not be blank')

    if request.form['email'].strip() != '' and not looksLikeEmailAddress(request.form['email'].strip()):
        goodForm = False
        flash("That doesn't look like a valid email address")

    # client name must not be blank
    if not request.form.get('name'):
        goodForm = False
        flash("You must provide a Client Name")
        
    return goodForm
    