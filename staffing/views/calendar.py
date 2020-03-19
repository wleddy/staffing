from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
     
from shotglass2.mapping.views.maps import simple_map
from shotglass2.shotglass import get_site_config
from shotglass2.users.models import User
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string, local_datetime_now, getDatetimeFromString
from staffing.models import Event, Location, ActivityGroup
from staffing.views.activity import get_event_recs
from staffing.views.signup import get_job_rows

import calendar
from datetime import date, timedelta
from ical.ical import ICal


mod = Blueprint('calendar',__name__, template_folder='templates/calendar', url_prefix='')


def setExits():
    g.listURL = url_for('.display')
    # g.editURL = url_for('.edit')
    # g.deleteURL = url_for('.delete')
    g.title = 'Calendar'
    
    
@mod.route('calendar/<int:month>/')
@mod.route('calendar/<int:month>')
@mod.route('calendar/<int:month>/<int:year>/')
@mod.route('calendar/<int:month>/<int:year>')
@mod.route('calendar')
@mod.route('calendar/')
def display(month=None,year=None):
    setExits()
    site_config = get_site_config()
    g.title="Calendar"
    
    start_date = local_datetime_now()
    today = date(start_date.year,start_date.month,start_date.day)
    
    start_date = date(start_date.year,start_date.month,1)
    if month == None:
        month = start_date.month
    if year == None:
        year = start_date.year
        
    month = cleanRecordID(month)
    year = cleanRecordID(year)
    refresh = False
    
    if year < 1951 or year > 3000:
        year = start_date.year
        refresh = True
        
    if month < 1 or month > 12:
        month = start_date.month
        refresh = True
        
    if refresh:
        return redirect(url_for('.display')+"{}/{}".format(month,year))
            
    try:
        start_date = date(year,month,1)
    except:
        pass # use todays date
           
    #import pdb;pdb.set_trace()
    user_id = 0
    if g.user:
        try:
           user_id = User(g.db).get(g.user).id 
        except:
           pass
    
    eom = calendar.monthrange(start_date.year,start_date.month)[1]
    end_date = start_date.replace(day=eom)    
    
    #import pdb;pdb.set_trace()
    status_list = ['scheduled','cancelled','postponed'] # this may come from form in future
    status_list = "'" + "','".join(status_list) + "'" 
        
    where = """lower(event.status) in ({status_list}) and date(event.event_start_date,'localtime') >= date('{start_date}') and date(event.event_end_date,'localtime') <= date('{end_date}')
    and event.exclude_from_calendar = 0
    """.format(
        status_list=status_list,
        start_date=start_date,
        end_date=end_date,
        )
    order_by = "event.event_start_date"
    
    event_data = Event(g.db).select(where = where, order_by=order_by, user_id=user_id)
    
    activity_groups = ActivityGroup(g.db).select()
    event_list_dict = {}
    if event_data:
        data_row = 0
        for event in event_data:
            event_date = getDatetimeFromString(event.event_start_date)
            if event_date:
                if event_date.day not in event_list_dict:
                    event_list_dict[event_date.day]=[]
                event_list_dict[event_date.day].append(data_row)
                
            data_row+=1
    
    # create a calendar object
    cal = calendar.Calendar(6)
    #get a list of lists of tuples
    cal_list=cal.monthdays2calendar(start_date.year,start_date.month)\
    ## some "constants for my sanity... the positions in the cal_list tuples"
    _cal_day = 0
    
    # add a list to each tuple to hold event_data index for each day
    for week in range(len(cal_list)):
        for day in range(7):
            if cal_list[week][day][_cal_day] != 0 and cal_list[week][day][_cal_day] in event_list_dict:
                cal_list[week][day] = cal_list[week][day] + (event_list_dict[cal_list[week][day][_cal_day]],)
            else:
                cal_list[week][day] = cal_list[week][day] + ([],)
        
    if month == 1:
        #go back to Dec of last year
        last_month = date(start_date.year-1,12,1)
        #go to Feb of this year
        next_month = date(start_date.year,2,1)
    elif month == 12:
        #go to Nov. of this year
        last_month = date(start_date.year,11,1)
        #go to Jan of next year
        next_month = date(start_date.year+1,1,1)
    else:
        # year does not change
        next_month = date(start_date.year,start_date.month+1,1)
        last_month = date(start_date.year,start_date.month-1,1)
        

    
    return render_template('calendar.html',
                            event_data=event_data,
                            calendar=calendar,
                            cal_list=cal_list,
                            start_date=start_date,
                            last_month=last_month,
                            next_month=next_month,
                            today = today,
                            activity_groups=activity_groups,
                            )


@mod.route('calendar/event/<int:event_id>')
@mod.route('calendar/event/<int:event_id>/')
@mod.route('calendar/event')
@mod.route('calendar/event/')
def event(event_id=None):
    """Return a page with the event details"""
    setExits()
    g.title = "Event Detail"
    #import pdb;pdb.set_trace()
    
    event_id = cleanRecordID(event_id)
    if event_id < 1:
        return redirect(url_for('.display'))
                        
    event = get_event_recs(event_id=event_id)
    
    if not event:
        return redirect(url_for('.display'))
        
    event = event[0]
    map_html = None
    event_locations = None

    # assemble a list of locations where this event will be held
    event_locations = Event(g.db).locations(event_id)
    # get the map for this
    map_data = []
    if event_locations:
        for loc in event_locations:
            # make a list of dict for the location
            map_data.append({'lat':loc.lat,'lng':loc.lng,
            'title':event.calendar_title,
            'description':event.event_description,
            'UID':str(event.event_id) + "-" + str(loc.id),
            'location_name':loc.location_name,
            },)
        map_html = simple_map(map_data,target_id='map')
        
    return render_template('calendar_event.html',event=event,map_html=map_html,event_locations=event_locations)
    
@mod.route('calendar/save_filter/<action>/<int:group_id>')
@mod.route('calendar/save_filter/<action>/<int:group_id>/')
@mod.route('calendar/save_filter/')
def save_group_filter(action='remove',group_id=0):
    """Save the users calendar filter prefs. We are actually saving the activity groups to 
    hide """
    # import pdb;pdb.set_trace()
    if not "calendar_group_filter" in session:
        session['calendar_group_filter']=[]
    if action == 'remove' and group_id in session['calendar_group_filter']:
        session['calendar_group_filter'].pop(session['calendar_group_filter'].index(group_id))
    if action == 'add'and group_id not in session['calendar_group_filter']:
        session['calendar_group_filter'].append(group_id)
        
    return 'Ok'
    
    
@mod.route('subscribe/<calendar_name>/',methods=['GET','PROPFIND','OPTIONS',])
@mod.route('subscribe/<calendar_name>',methods=['GET','PROPFIND','OPTIONS',])
@mod.route('subscribe',methods=['GET','PROPFIND','OPTIONS',])
@mod.route('subscribe/',methods=['GET','PROPFIND','OPTIONS',])
def subscribe(calendar_name=''):
    """Return an icalendar text. """
    # import pdb;pdb.set_trace()
    site_config = get_site_config()
    if not calendar_name:
        calendar_name = site_config['SITE_NAME']
    ical = ICal(calendar_name=calendar_name)
    
    recs = Event(g.db).select(where="event.event_start_date > datetime('{}')".format(local_datetime_now() - timedelta(days=30)))
    
    if recs:
        for rec in recs:
            ical.add_event(
                "{}.{}.{}".format(
                rec.id,
                rec.activity_id,
                site_config['HOST_NAME']
                ),
               rec.event_start_date,
               rec.event_end_date,
                rec.event_title,
                url = request.url_root,
            )
    
    return ical.get()
    
    