# Send communications to users
from flask import g
from shotglass2.shotglass import get_site_config
from shotglass2.takeabeltof.date_utils import getDatetimeFromString, local_datetime_now, datetime_as_string
from shotglass2.takeabeltof.utils import render_markdown_for, printException
from shotglass2.takeabeltof.mailer import send_message, email_admin
from shotglass2.users.models import User
from staffing.models import StaffNotification, Job, Event, UserJob
from datetime import datetime, timedelta


def send_signup_email(job_data,user,template_path,bp,**kwargs):
    """Send an email confirming a single user's signup
    currently this only generates one email
    param: job_data is the result of the query in staffing.signup.get_job_rows (a list of recs)
    param: user is a single instance of a User record
    param: template_path, obviously the path to a template... but absolute or relative to what?
    param: bp, the Blueprint for the template. May be None
    
    'subject' may be included in kwargs
    if 'cancellation' is in kwargs, this is a notice of cancellation do don't include the ical attachement
    
    if values are supplied in kwargs they are passed to the template as additional context
    """
    #import pdb;pdb.set_trace()
    uid=get_uid(job_data,user)
    location = get_location(job_data)
    geo = get_geo(job_data)    
    description = get_description(job_data,geo,location)
    ical = None
    
    if not kwargs.get('cancellation',False):            
        ical_event = make_event_dict(uid,job_data.start_date,job_data.end_date,job_data.job_title,
                description=description.replace('\n\n','\n'),
                location=location,
                geo=geo,
                )

        ical = get_ical_text(events=ical_event)
    
    # generate the text of the email with ical as an attachment
    email_html = render_markdown_for(template_path,
        bp=bp,
        ical=ical,
        description=description,
        job_data=job_data,
        **kwargs
        )
        
    subject = kwargs.pop('subject','')
    if not subject:
        subject = 'Your assignment for {}'.format(job_data.event_title)
    attachment = None
    if ical:
        attachment = ("{}.ics".format(job_data.job_title.replace(' ','_')), "text/calendar", ical)
            
    # send that puppy!
    send_result = send_message([(user.email,' '.join([user.first_name,user.last_name]))],
                    subject=subject,
                    body_is_html=True,
                    body=email_html,
                    attachment=attachment,
                    )
    if not send_result[0]:
        #Error occured
        email_admin(subject="Error sending signup confirmation at {}".format(get_site_config()['SITE_NAME']),message="An error occored while trying to send signup email. Err: {}".format(send_result[1]))
    
    
def process_two_day_reminder():
    """Just what is says.
    Send a reminder notice to all volunteers and staff who have a 
    job scheduled in the next two days"""
    
    import pdb;pdb.set_trace()
    
    from staffing.views.signup import mod as signup_blueprint, get_job_rows
    
    try:
        now = local_datetime_now()
        start_date = datetime_as_string(now)
        end_date = datetime_as_string(now + timedelta(days=2))
        
        #for testing...
        start_date = '2019-03-01'
        end_date = '2019-03-30'
        
        
        trigger_function_name = "annoucements.send_two_day_reminder"
        notifications = StaffNotification(g.db)
        userjobs = UserJob(g.db)
    
        # Get all jobs that are to start today ago or up to 2 days from now
        sql = """
        select
        user_job.user_id,
        user_job.job_id,
        job.start_date as job_start_date

        from user_job
        join user on user.id = user_job.user_id
        join job on job.id = user_job.job_id

        where 
            date(job_start_date,'localtime') >= date('{}','localtime') and
            date(job_start_date,'localtime') <= date('{}','localtime') 
    
        order by
            user_job.user_id,
            job_start_date
        """.format(start_date,end_date)
        
        reminder_jobs = userjobs.query(sql)
        if reminder_jobs:
            prev_user_id = None
            job_list = []
            for reminder in reminder_jobs:
                # for each user compile a list of jobs to which they are assigned for which no notification has been sent
                if prev_user_id == None:
                    #first record
                    prev_user_id = reminder.user_id
                    
                if reminder.user_id != prev_user_id:
                    user_rec = User(g.db).get(prev_user_id) 
                    if len(job_list) > 0 and user_rec:
                            # send a reminder for the current user and job list
                            subject = "Two Day Job Reminder"
                            template_path = 'announce/email/two_day_reminder.md'
                            job_list_as_string = ','.join([str(x) for x in job_list])
                            job_data = get_job_rows(None,None,"job.id in ({})".format(job_list_as_string),[],is_admin=True)
                            
                            send_result = send_signup_email(job_data,user_rec,template_path,signup_blueprint,subject=subject)
                            if send_result[0]:
                                #send Ok, create some notification records
                                for job in job_list:
                                    rec = notifications.new()
                                    rec.user_id = prev_user_id
                                    rec.job_id = job
                                    rec.trigger_function_name = trigger_function_name
                                    rec.run_date = now
                                    notifications.save(rec)
                                g.db.commit()
                            else:
                                email_admin('Unable to send two day reminder to {}. Result: {}'.format((user_rec.first_name + ' ' + user_rec.last_name),send_result[1]))
                                    
                    prev_user_id = reminder.user_id
                    job_list = []
                        
                # add job to job_list?
                #test the log
                where = 'user_id = {} and job_id = {} and trigger_function_name = "{}"'.format(reminder.user_id,reminder.job_id,trigger_function_name)
                if not notifications.select(where=where):
                    # No notification record found
                    job_list.append(reminder.job_id)

    except Exception as e:
        mes = "An error occured while processing 2 Day renimders. Err: {}".format(str(e))
        printException(mes)
        email_admin(mes)
        
    
def get_ical_text(events):
    """Return the text of an icalendar object or None
    @param events = a list of dictionaries that each describ an event
        
    """
    from icalendar import Calendar, Event as IcalEvent
    #import pdb;pdb.set_trace()

    out = None
    if not isinstance(events,list):
        events = [events]
 
    calendar = Calendar()
    calendar.add('version','2.0')
    calendar.add('calscale','GREGORIAN')
    calendar.add('prodid','net.williesworkshop.calendar')
    calendar.add('x-priamry-calendar','TRUE')

    event_count = 0
    for event in events:
        if event:
            ev = IcalEvent()
        
            minumum_properties = True
            # Minimum required properties
            for key in ['uid','dtstart','dtend','summary',]:
                if key not in event:
                    minumum_properties = False
                    break
                value = event.pop(key)
                if isinstance(value,str) and key in ['dtstart','dtend',]:
                    value = getDatetimeFromString(value)
                
                ev.add(key,value)
            
            if not minumum_properties:
                break
            
            for key, value in event.items():
                if value:
                    ev.add(key,value)
            
            ev.add('DTSTAMP',local_datetime_now('UTC'))
            calendar.add_component(ev)
            event_count += 1
        
    if event_count > 0:
        out = calendar.to_ical()

    return out


def make_event_dict(uid,start,end,summary,**kwargs):
    """Return a dictionary suitable for use when creating a calendar event"""
    ical_event = {}
    # the required fields
    ical_event['uid'] = uid
    ical_event['dtstart'] = start
    ical_event['dtend'] = end
    ical_event['summary'] = summary

    for key, value in kwargs.items():
        ical_event[key] = value
    
    return ical_event

def get_description(job_data,geo,location):
    """Return the description text for the job"""
    description = ''
    
    if job_data.job_loc_name:
        location = job_data.job_loc_name
        description += 'Location:\n\n{}'.format(job_data.job_loc_name)

    if  job_data.job_loc_street_address and job_data.job_loc_city and job_data.job_loc_state:
        if description:
            description += '\n\n'
        description += '{}  {}'.format(', '.join([job_data.job_loc_street_address, job_data.job_loc_city]), job_data.job_loc_state.upper())

    w3w_map_url = google_map_url = None
    
    if job_data.job_loc_w3w:
        w3w_map_url = 'https://w3w.co/{}'.format(job_data.job_loc_w3w)
        
    # Create a mapping uri for google maps
    # Include maps for both w3w and goggle maps, let user decide
    if geo:
        # don't replace the w3w link
        google_map_url = "https://www.google.com/maps/search/?api=1&query={},{}".format(geo[0],geo[1])
        
    if description and (w3w_map_url or google_map_url):
        description += '\n\n'
    if w3w_map_url:
        description += 'W3W Map: {}\n\n\n'.format(w3w_map_url)
    if google_map_url:
        description += 'Google Map: {}\n\n'.format(google_map_url)
            
    if description:
        description += '\n\n'
    description += job_data.event_description + '\n\n' + job_data.job_description
    
    return description
    
def get_geo(job_data):
    if job_data.job_loc_lat and job_data.job_loc_lng:

        ### Apple Calender does not seem to use geo to set map location
        ### it uses the value in location to try a reverse geocode lookup
        return (job_data.job_loc_lat,job_data.job_loc_lng)
        
    return None
    
    
def get_location(job_data):
    location = ''
    # if job_data.job_loc_name:
    #     location = job_data.job_loc_name

    if  job_data.job_loc_street_address and job_data.job_loc_city and job_data.job_loc_state:
        if location:
            ## the location name may be getting prepended to the address without any
            ##   separation on Android calendar.
            ##   Just hang a comma on the end to force some kind of separation
            location += ', \n'
            
        location = location + '{}  {}'.format(', '.join([job_data.job_loc_street_address, job_data.job_loc_city]), job_data.job_loc_state.upper())

    return location

def get_uid(job_data,user):
    return '{}_{}_{}'.format(
           '000000{}'.format(job_data.event_id)[-6:],
           '000000{}'.format(job_data.job_id)[-6:],
           '000000{}'.format(user.id)[-6:],
           )
