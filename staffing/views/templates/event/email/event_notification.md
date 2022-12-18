## A message from {{ session.user_name }} at {{ site_config.ORG_NAME | default(site_config.SITE_NAME, True) }}

### RE: {{ event.event_title }}

### Subject: 

{{ form.subject | safe }}

### Message:

{{ form.message | safe }}


{% if job_data_list and not no_calendar %}

{% include "announce/email/addendum.md" %}

---
If you are unable to make it to any of your events, please contact the Event Manager using the 
contact links below as soon as possible so we can arrange for someone to take your place.

{% for job_data in job_data_list %}

### {{ job_data.activity_title }}
#### _{{ job_data.job_title }}_

> Your assignment date: {{ job_data.start_date | abbr_date_string }}

> Your shift starts at {{ job_data.start_date | local_time_string }}
> and ends at {{ job_data.end_date | local_time_string }}.

> Location: {{job_data.job_loc_name | default('tbd',True) }}  

> Questions about this shift? [Contact Event Manager](http://{{config.HOST_NAME}}{{ url_for('signup.contact_event_manager')}}{{ job_data.job_id | default('',True) }}/).

---
{% endfor %}

{% if ical %}
The attached file(s) will add (or update) your shifts on your calendar. 

(Usually you can tap or double click to open it.)
{% endif %}

{% endif %}

