from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.mapping.views.maps import simple_map
from shotglass2.shotglass import get_site_config
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string, local_datetime_now, getDatetimeFromString
from staffing.models import Event, Location, ActivityType
from staffing.views.signup import get_job_rows

import calendar
from datetime import date, timedelta

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
    
    eom = calendar.monthrange(start_date.year,start_date.month)[1]
    end_date = start_date.replace(day=eom)    
    
    job_data = get_job_rows(start_date,end_date,is_admin=True,
            event_status_where=get_event_status_where(),
            where=" event.exclude_from_calendar = 0 ",
            order_by="date(event.event_start_date,'localtime')",
            group_by=" event.id ",)
            
    job_list_dict = {}
    if job_data:
        data_row = 0
        for job in job_data:
            job_date = getDatetimeFromString(job.start_date)
            if job_date:
                if job_date.day not in job_list_dict:
                    job_list_dict[job_date.day]=[]
                job_list_dict[job_date.day].append(data_row)
                
            data_row+=1
    
    # create a calendar object
    cal = calendar.Calendar(6)
    #get a list of lists of tuples
    cal_list=cal.monthdays2calendar(start_date.year,start_date.month)\
    ## some "constants for my sanity... the positions in the cal_list tuples"
    _cal_day = 0
    
    # add a list to each tuple to hold job_data index for each day
    for week in range(len(cal_list)):
        for day in range(7):
            if cal_list[week][day][_cal_day] != 0 and cal_list[week][day][_cal_day] in job_list_dict:
                cal_list[week][day] = cal_list[week][day] + (job_list_dict[cal_list[week][day][_cal_day]],)
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
                            job_data=job_data,
                            calendar=calendar,
                            cal_list=cal_list,
                            start_date=start_date,
                            last_month=last_month,
                            next_month=next_month,
                            today = today,
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
        
    job = get_job_rows(None,None,is_admin=True,where="job.event_id = {}".format(event_id),
                        event_status_where=get_event_status_where(),
                        )
    if not job:
        return redirect(url_for('.display'))
        
    job = job[0]
    map_html = None
    
    # get the map for this
    if job.job_loc_lat and job.job_loc_lng:
        # make a list of dict for the location
        map_data = {'lat':job.job_loc_lat,'lng':job.job_loc_lng,
        'title':job.activity_title,
        'description':job.event_description,
        'UID':job.event_id,
        'location_name':job.job_loc_name,
        }
        map_html = simple_map(map_data,target_id='map')
        
    return render_template('calendar_event.html',job=job,map_html=map_html,)
    
    
def get_event_status_where():
    return " and lower(event.status) = 'scheduled' "