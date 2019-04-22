from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint
from shotglass2.shotglass import get_site_config
from shotglass2.users.admin import login_required, table_access_required
from shotglass2.takeabeltof.utils import render_markdown_for, printException, cleanRecordID
from shotglass2.takeabeltof.date_utils import datetime_as_string, local_datetime_now, getDatetimeFromString
from staffing.models import Event, Location, EventType
from staffing.views.signup import get_job_rows

import calendar
from datetime import date, timedelta

mod = Blueprint('calendar',__name__, template_folder='templates/calendar', url_prefix='')


def setExits():
    g.listURL = url_for('.display')
    # g.editURL = url_for('.edit')
    # g.deleteURL = url_for('.delete')
    g.title = 'Calendar'


@mod.route('calendar',methods=['GET','POST',])
@mod.route('calendar/',methods=['GET','POST',])
def display():
    setExits()
    site_config = get_site_config()
    g.title="{} Calendar".format(site_config.get('ORG_NAME','Our'))
    
    start_date = local_datetime_now()
    start_date = date(start_date.year,start_date.month,1)
    if request.form:
        try:
            start_date = date(int(request.form['year']),int(request.form['month']),1)
        except:
            pass # use todays date
            
    end_date = start_date + timedelta(days=calendar.monthrange(start_date.year,start_date.month)[1])
    
    
    #import pdb;pdb.set_trace()
        
    job_data = get_job_rows(start_date,end_date,is_admin=True,
            job_status_where=" and lower(job.status) = 'public calendar' ",
            order_by="date(job.start_date,'localtime')")
            
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
    cal_day = 0
    cal_weekday_num = 1
    cal_data_index = 2
    
    # add a list to each tuple to hold job_data index for each day
    for week in range(len(cal_list)):
        for day in range(7):
            if cal_list[week][day][cal_day] != 0 and cal_list[week][day][cal_day] in job_list_dict:
                cal_list[week][day] = cal_list[week][day] + (job_list_dict[cal_list[week][day][cal_day]],)
            else:
                cal_list[week][day] = cal_list[week][day] + ([],)

    return render_template('calendar.html',job_data=job_data,calendar=calendar,cal_list=cal_list,start_date=start_date)
