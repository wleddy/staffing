# Send communications to users
from shotglass2.shotglass import get_site_config
from shotglass2.takeabeltof.date_utils import getDatetimeFromString, local_datetime_now
from shotglass2.takeabeltof.utils import render_markdown_for
from shotglass2.takeabeltof.mailer import send_message, email_admin


def send_signup_email(job_data,user,template_path,bp,**kwargs):
    """Send an email confirming a single user's signup
    currently this only generates one email
    param: job_data is the result of the query in staffing.signup.get_job_rows (a list of recs)
    param: user is a single instance of a User record
    param: template_path, obviously the path to a template... but absolute or relative to what?
    
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

        ical = get_ical_text(event=ical_event)
    
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
    
    
def get_ical_text(**kwargs):
    """Return the text of an icalendar object or None"""
    from icalendar import Calendar, Event
    #import pdb;pdb.set_trace()

    event = kwargs.get('event',None) # a dict of event data
    events = kwargs.get('events',None) # a list of event dicts
    out = None

    if events:
        if not isinstance(events,list):
            events = [events]
        events.extend([event])
    elif event:
        events = [event]

    calendar = Calendar()
    calendar.add('version','2.0')
    calendar.add('calscale','GREGORIAN')
    calendar.add('prodid','net.williesworkshop.calendar')
    calendar.add('x-priamry-calendar','TRUE')

    event_count = 0
    for event in events:
        if event:
            ev = Event()
        
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
    description = job_data.event_description + '\n\n' + job_data.job_description
    if job_data.job_loc_name:
        location = job_data.job_loc_name
        description += '\n\n*location:*\n\n{}'.format(job_data.job_loc_name)

    if  job_data.job_loc_street_address and job_data.job_loc_city and job_data.job_loc_state:
        description += '\n\n{}  {}'.format(', '.join([job_data.job_loc_street_address, job_data.job_loc_city]), job_data.job_loc_state.upper())

    map_url = None
    
    if job_data.job_loc_w3w:
        map_url = 'https://w3w.co/{}'.format(job_data.job_loc_w3w)
        
        
        # Create a mapping uri
        ############################
        ## TODO - This should place a pin at least
        ##        Maybe try to use apple maps if on iOS
        ############################
        if not map_url and geo:
            # don't replace the w3w link
            map_url = "https://www.google.com/maps/place/@{},{},17z".format(geo[0],geo[1])
        
    if map_url:
        description = description + '\n\n' + 'Map: {}'.format(map_url)
    
    return description
    
def get_geo(job_data):
    if job_data.job_loc_lat and job_data.job_loc_lng:

        ### Apple Calender does not seem to use geo to set map location
        ### it uses the value in location to try a reverse geocode lookup
        return (job_data.job_loc_lat,job_data.job_loc_lng)
        
    return None
    
    
def get_location(job_data):
    location = ''
    if job_data.job_loc_name:
        location = job_data.job_loc_name

    if  job_data.job_loc_street_address and job_data.job_loc_city and job_data.job_loc_state:
        if location:
            location += '\n\n'
        location = location + '{}  {}'.format(', '.join([job_data.job_loc_street_address, job_data.job_loc_city]), job_data.job_loc_state.upper())

    return location

def get_uid(job_data,user):
    return '{}_{}_{}'.format(
           '000000{}'.format(job_data.event_id)[-6:],
           '000000{}'.format(job_data.job_id)[-6:],
           '000000{}'.format(user.id)[-6:],
           )
