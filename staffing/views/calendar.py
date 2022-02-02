from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
     
from shotglass2.mapping.views.maps import simple_map
from shotglass2.shotglass import get_site_config
from shotglass2.users.models import User, UserRole
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.mailer import send_message, email_admin
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string, local_datetime_now, getDatetimeFromString, date_to_string
from staffing.models import Event, Location, ActivityGroup, Job, JobRole
from staffing.views.activity import get_event_recs
from staffing.views.signup import get_job_rows, get_volunteer_role_ids

import calendar
from datetime import datetime, date, timedelta
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

    #try to get the month and year from session if not provided
    if month == None or year == None:
        try:
            if session['calendar_last_access'] < today.toordinal():
                raise KeyError
            month = session["calendar_month"]
            year = session["calendar_year"]
        except (KeyError, TypeError):
            month = start_date.month
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
        
    # add the last settings to the session
    session['calendar_last_access'] = today.toordinal()
    session["calendar_year"] = year
    session["calendar_month"] = month
        
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
            # events may span multiple days
            event_end = getDatetimeFromString(event.event_end_date)
            if event_date and event_end and event_date <= event_end:
                while event_date <= event_end:
                    if event_date.day not in event_list_dict:
                        event_list_dict[event_date.day]=[]
                    event_list_dict[event_date.day].append(data_row)
                    event_date = event_date + timedelta(days=1)
                
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
    # import pdb;pdb.set_trace()
    
    event_id = cleanRecordID(event_id)

    event = get_event_recs(event_id=event_id)
    
    if not event:
        return redirect(url_for('.display'))
        
    event = event[0]
    g.title=event.service_type
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
        
    # determine if user has a role that would allow them to signup for any job in this event
    # import pdb;pdb.set_trace()
    
    has_required_role = False
    temp_user_id = 0
    vol_roles = [int(x) for x in get_volunteer_role_ids().split(",")]
    
    try:
        temp_user_id = session["user_id"]
    except KeyError:
        pass
        
    jobs = Job(g.db).select(where="event_id = {event_id}".format(event_id=event.event_id))
    if jobs:
        job_list = ",".join([str(x.id) for x in jobs])
        roles = JobRole(g.db).select(where="job_id in ({job_list})".format(job_list=job_list))
        if roles:
            # if volunteer roles are in the role_list everyone is qualified
            for role in roles:
                if role.role_id in vol_roles:
                    has_required_role = True
                    break
                    
            if not has_required_role:
                # test to see if the user has other required roles
                role_list = ",".join([str(x.role_id) for x in roles])
                if UserRole(g.db).select(where="user_id = {user_id} and role_id in ({role_list})".format(
                            user_id=temp_user_id,
                            role_list=role_list,
                            )):
                    has_required_role = True

    return render_template('calendar_event.html',
        event=event,
        map_html=map_html,
        event_locations=event_locations,
        has_required_role = has_required_role,
        )
    
    
@mod.route('calendar/event_calendar_item/<int:event_id>',methods=['GET',])
@mod.route('calendar/event_calendar_item/<int:event_id>/',methods=['GET',])
@mod.route('calendar/event_calendar_item/',methods=['GET',])
def event_calendar_item(event_id=None):
    #download an ical text for the specified event
    
    filename=None
    ical=None
    calendar_name="calendar"
    rec = Event(g.db).select_one(where="event.id = {}".format(cleanRecordID(event_id)))
    if rec:
        ical = get_ical_text(calendar_name,rec)
        filename = calendar_name = rec.event_title
        
    return ical_response(ical,filename)
    
    
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
    
    
@mod.route('calendar/subscribe/<calendar_name>/',methods=['GET',])
@mod.route('calendar/subscribe/<calendar_name>',methods=['GET',])
@mod.route('calendar/subscribe',methods=['GET',])
@mod.route('calendar/subscribe/',methods=['GET',])
def subscribe(calendar_name=''):
    """download an icalendar file"""
    
    setExits()
    g.title = "Calendar Subscription"
    
    # import pdb;pdb.set_trace()
    site_config = get_site_config()
    if not calendar_name:
        calendar_name = site_config['SITE_NAME']

    where="datetime(event.event_start_date,'localtime') > datetime('{}','localtime')".format(datetime_as_string(local_datetime_now() - timedelta(days=30)))
    where += " and event.exclude_from_calendar = 0 "
    where += " and lower(event.status) <> 'pending' "
    recs = Event(g.db).select(where = where)
    # import pdb;pdb.set_trace()
    
    ical = get_ical_text(calendar_name,recs) # return some ical text or None
    filename = calendar_name.replace(' ','_')
    return ical_response(ical,filename)
    
    
@mod.route('calendar/subscribe/summary/<calendar_name>/',methods=['GET',])
@mod.route('calendar/subscribe/summary/<calendar_name>',methods=['GET',])
@mod.route('calendar/subscribe/summary',methods=['GET',])
@mod.route('calendar/subscribe/summary/',methods=['GET',])
def subscribe_to_summary(calendar_name=''):
    """download an icalendar file where events are summeraized as all day event
    entries in the calendar. 
    
    The goal is to not clutter up the users calendar too much.
    """

    def create_event(ical,cal_date,description):
        summary = "{} Events for {}".format(site_config["MAIL_SUBJECT_PREFIX"],date_to_string(cal_date,'date'))
        ical.add_event(
            "{}.{}.{}".format(
            cal_date,
            site_config['HOST_NAME'],
            calendar_name,
            ),
           cal_date,
           cal_date,
           summary,
           description=description,
           reminder=True, # Default 30 minute reminder
        )
        

    # import pdb;pdb.set_trace()
    site_config = get_site_config()
    if not calendar_name:
        calendar_name = site_config['SITE_NAME']
    ical = ICal(calendar_name=calendar_name)
    where="datetime(event.event_start_date,'localtime') > datetime('{}','localtime')".format(datetime_as_string(local_datetime_now() - timedelta(days=30)))
    where += " and event.exclude_from_calendar = 0 "
    where += " and lower(event.status) <> 'pending' "
    recs = Event(g.db).select(where = where,order_by = "event.event_start_date")
    
    # import pdb;pdb.set_trace()

    if recs:
        prev_date = None
        description = ''
        for rec in recs:
            # did the date change?
            rec_date = datetime.date(getDatetimeFromString(rec.event_start_date))
            if not prev_date or rec_date != prev_date:
                if description !='':
                    # there is something to output
                    create_event(ical,prev_date,description)
                    description = ''
                    
                prev_date = rec_date
            #Add some content to the description
            url = request.url_root.rstrip('/') + url_for('calendar.event') + str(rec.id) + '/'
            calendar_status = ''
            if rec.status.lower() != 'scheduled': 
                calendar_status = '!' + rec.status.upper() + '! '
                
            description += """{calendar_status} {title} 
{start} - {end} 
{url} 
""".format(
                calendar_status=calendar_status,
                title = rec.event_title,
                start = date_to_string(rec.event_start_date,'local_time'),
                end = date_to_string(rec.event_end_date,'local_time'),
                url=url,
            )
            
        if description != '':
            #add the last event
            create_event(ical,prev_date,description)
                
        ical = ical.get()
            
        return ical_response(ical,calendar_name)

    
def get_ical_text(calendar_name,event_recs):
    # return an ical text object or None for event_recs
    if not isinstance(calendar_name,str):
        calendar_name = "calendar"
    ical = ICal(calendar_name=calendar_name)

    site_config = get_site_config()
    
    if event_recs:
        if not isinstance(event_recs,list):
            event_recs = [event_recs]
        
        for rec in event_recs:
            locations = Event(g.db).locations(rec.id)
            event_location = 'tbd'
            geo = None
            if locations and len(locations) == 1:
                event_location = "{}, {} {}".format(locations[0].street_address,locations[0].city,locations[0].state)
                geo = (locations[0].lat,locations[0].lng)
            elif locations and len(locations) > 1:
                event_location = "Multiple Locations"
            url = request.url_root.rstrip('/') + url_for('calendar.event') + str(rec.id) + '/'
            calendar_status = rec.status.upper()
            calendar_method = 'PUT'
            sequence = 1
            if rec.exclude_from_calendar == 1:
                calendar_status = "CANCELLED" # Incase it was in the calendar before.
                calendar_method = 'CANCEL'
                sequence = 2000
            summary_status = ''
            if rec.status.lower() != 'scheduled': 
                summary_status = '!' + rec.status.upper() + '! '
            summary = "{} {}{}".format(site_config["MAIL_SUBJECT_PREFIX"],summary_status,rec.event_title)
            ical.add_event(
                "{}.{}.{}".format(
                rec.id,
                rec.activity_id,
                site_config['HOST_NAME'] + calendar_name
                ),
               rec.event_start_date,
               rec.event_end_date,
               summary,
               url = url,
               description=rec.event_description,
               location = event_location,
               status=calendar_status,
               method=calendar_method,
               sequence=sequence,
               geo=geo,
               reminder=True, # Default 30 minute reminder
            )
        ical = ical.get()
        
    return ical
    
def ical_response(ical,filename):
    # return a Responce object with the sepecifred ical text or some error text
    calendar_name = "calendar_item"
    if filename and isinstance(filename,str):
        calendar_name = filename.replace(' ','_').replace("&","_")
        
    if ical:            
        headers={
           "Content-Disposition":"attachment;filename={}.ics".format(calendar_name),
            }

        return Response(
                ical,
                mimetype="text/calendar",
                headers=headers
                )
         
    
    return "No Events found..."
    