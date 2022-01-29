# Send communications to users
from flask import g
from ical.ical import ICal
from shotglass2.shotglass import get_site_config
from shotglass2.takeabeltof.date_utils import getDatetimeFromString, local_datetime_now, datetime_as_string
from shotglass2.takeabeltof.utils import render_markdown_for, printException
from shotglass2.takeabeltof.mailer import Mailer, send_message, email_admin
from shotglass2.users.models import User, Pref
from staffing.models import StaffNotification, Job, Event, UserJob
from datetime import datetime, timedelta


def send_signup_email(job_data_list,user,template_path,bp,**kwargs):
    """Send an email confirming a single user's signup
    currently this only generates one email
    param: job_data is the result of the query in staffing.signup.get_job_rows (a list of recs)
    param: user is a single instance of a User record
    param: template_path, obviously the path to a template... but absolute or relative to what?
    param: bp, the Blueprint for the template. May be None
    
    'subject' may be included in kwargs
    if 'no_calendar' is in kwargs, do don't include the ical attachement
    
    if values are supplied in kwargs they are passed to the template as additional context
    """
    # import pdb;pdb.set_trace()
    if not isinstance(job_data_list,list):
        job_data_list = [job_data_list]
            
            
    site_config = get_site_config()
            
    # import pdb;pdb.set_trace()
            
    ical = None
    ical_events = []
    for job_data in job_data_list:
        uid=get_uid(job_data,user)
        location = get_location(job_data)
        geo = get_geo(job_data)    
        description = get_description(job_data,geo,location)
    
        if not kwargs.get('no_calendar',False):            
            ical_events.append(make_event_dict(uid,job_data.start_date,job_data.end_date,job_data.job_title,
                    description=description.replace('\n\n','\n'),
                    location=location,
                    geo=geo,
                    reminder=True, # Default 30 minute reminder
                    )
                )

    if ical_events:
        ical = get_ical_text(events=ical_events)
    
    # generate the text of the email with ical as an attachment
    email_html = render_markdown_for(template_path,
        bp=bp,
        ical=ical,
        description=description,
        job_data_list=job_data_list,
        user=user,
        **kwargs
        )
            

    subject = kwargs.pop('subject','')
    if not subject:
        subject = 'Your assignment for {}'.format(job_data.activity_title)
    attachment = None
    if ical:
        attachment = ("{}.ics".format(job_data.job_title.replace(' ','_')), "text/calendar", ical)
            
    #import pdb;pdb.set_trace()
    bcc = None
    if site_config.get('BCC_ADMINS_ON_ALL_EMAIL',False):
        bcc=site_config.get('ADMIN_EMAILS',None)
        
    # send that puppy!
    mailer = Mailer(**kwargs)
    mailer.add_address((user.email,' '.join([user.first_name,user.last_name])))
    mailer.add_bcc(bcc)
    mailer.subject = subject
    mailer.body = email_html
    mailer.body_is_html = True
    mailer.add_attachment(attachment)
    
    mailer.send()
    if not mailer.success:
        #Error occured
        email_admin(subject="Error sending signup confirmation at {}".format(get_site_config()['SITE_NAME']),message="An error occored while trying to send signup email. Err: {}".format(mailer.result_text))
    
    # for now... just to support old code
    return (mailer.success,mailer.result_text)
    
    
def process_commitment_reminder():
    """Just what is says.
    Send a reminder notice to all volunteers and staff who have a 
    job scheduled in the next few days"""
    
    #import pdb;pdb.set_trace()
    
    from staffing.views.signup import mod as signup_blueprint, get_job_rows
    
    try:
        
        def send_reminder(user_id,job_list):
            user_rec = User(g.db).get(user_id) 
            if len(job_list) > 0 and user_rec:
                    # send a reminder for the current user and job list
                    subject = "Commitment Reminder"
                    template_path = 'announce/email/commitment_reminder.md'
                    job_list_as_string = ','.join([str(x) for x in job_list])
                    job_data = get_job_rows(None,None,"job.id in ({})".format(job_list_as_string),[],is_admin=True)
                    
                    # the most likely reason for not job_data is case where status of all jobs in list is not "active"
                    if job_data:
                        send_result = send_signup_email(job_data,user_rec,template_path,signup_blueprint,subject=subject,escape=False)
                        if send_result[0]:
                            #send Ok, create some notification records
                            log_notifications(job_list,prev_user_id,trigger_function_name)
                        else:
                            email_admin('Unable to send commitment reminder to {}. Result: {}'.format((user_rec.first_name + ' ' + user_rec.last_name),send_result[1]))
            
            
        now = local_datetime_now()
        start_date = datetime_as_string(now)
        reminder_days = int(Pref(g.db).get('Commitment Reminder Days',default=2).value)
        end_date = datetime_as_string(now + timedelta(days=reminder_days))
        
        ###for testing
        ##start_date = '2019-03-01'
        ##end_date = '2019-04-01'
                
        trigger_function_name = "annoucements.send_commitment_reminder"
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
                    send_reminder(prev_user_id,job_list)
                    prev_user_id = reminder.user_id
                    job_list = []
                        
                # add job to job_list?
                #test the log
                where = 'user_id = {} and job_id = {} and trigger_function_name = "{}"'.format(reminder.user_id,reminder.job_id,trigger_function_name)
                if not notifications.select(where=where):
                    # No notification record found
                    job_list.append(reminder.job_id)
                    
            # check that there is nothing in the chamber
            if job_list:
                send_reminder(reminder.user_id,job_list)

    except Exception as e:
        mes = "An error occured while processing commitment renimders. Err: {}".format(str(e))
        printException(mes)
        email_admin(mes)
        
    
def log_notifications(job_list,user_id,trigger_function_name):
    """Create StaffNotification records for the job ids in job_list
    @param job_list = list of integer job ids
    @param user_id = id of a user assigned to the job
    @param trigger_function_name = the name of the method that sent the noticication
    """
    if not isinstance(job_list,list):
        job_list = [job_list]
        
    now = local_datetime_now()
    notifications = StaffNotification(g.db)
    
    for job in job_list:
        job_rec = Job(g.db).get(job)
        rec = notifications.new()
        rec.user_id = user_id
        rec.job_id = job
        if job_rec:
            rec.event_id = job_rec.event_id
        rec.trigger_function_name = trigger_function_name
        rec.run_date = now
        notifications.save(rec)
    g.db.commit()
                                
                                
def get_ical_text(events):
    """Return the text of an icalendar object or None
    @param events = a list of dictionaries that each describe an event
        
    """

    # import pdb;pdb.set_trace()
    calendar = ICal()

    if not isinstance(events,list):
        events = [events]

    for event in events:
        if event:
            minumum_properties = True
            # Minimum required properties
            for key in ['uid','dtstart','dtend','summary',]:
                if key not in event:
                    minumum_properties = False
                    break
            if minumum_properties:
                calendar.add_event(event.pop('uid'),event.pop('dtstart'),event.pop('dtend'),event.pop('summary'),**event)
             
    return calendar.get()


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
