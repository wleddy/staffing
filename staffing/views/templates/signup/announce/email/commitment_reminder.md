{% from '_staffing_helper_macros.html' import directions_snippet %}

{% if renminder_type == 'future' %}
## Your Future {{ 'commitment' | plural(job_data_list) }} for {{ site_config.ORG_NAME | default(site_config.SITE_NAME, True) }}

You have the following {{ 'commitment' | plural(job_data_list) }} coming up.

{% else %}
## Your Reminder from {{ site_config.ORG_NAME | default(site_config.SITE_NAME, True) }}

You have the following commitments coming up in the next few days.
{% endif %}

If you are unable to make it to any of the events, please contact the Event Manager using the 
contact links below as soon as possible so we can arrange for someone to take your place.

{% if job_data_list %}
---
{% for job_data in job_data_list %}

### {{ job_data.activity_title }}
#### _{{ job_data.job_title }}_

> Your assignment date: {{ job_data.start_date | abbr_date_string }}

> Your shift starts at {{ job_data.start_date | local_time_string }}
> and ends at {{ job_data.end_date | local_time_string }}.

> Location: {{job_data.job_loc_name | default('tbd',True) }}  

{% include "announce/email/addendum.md" %}

> Questions about this shift? [Contact Event Manager](http://{{config.HOST_NAME}}{{ url_for('signup.contact_event_manager')}}{{ job_data.job_id | default('',True) }}/).

{{ directions_snippet(job_data) }}

---
{% endfor %}

{% if ical %}
The attached file will add (or update) your shifts on your calendar. 

(Usually you can tap or double click to open it.)
{% endif %}

{% else %}
Hummm... something when wrong... there are no jobs listed.

{% endif %}

