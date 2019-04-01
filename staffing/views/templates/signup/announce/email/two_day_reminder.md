## Your 2 Day Reminder from {{ site_config.ORG_NAME | default(site_config.SITE_NAME, True) }}

You have the following commitments coming up in the next couple days.

If you are unable to make it to any of the events, please [contact us](http://{{config.HOST_NAME}}{{ url_for('signup.contact')}})
as soon as possible so we can arrange for someone to take your place.

{% if job_data_list %}
{% for job_data in job_data_list %}
---
### {{ job_data.event_title }}
#### _{{ job_data.job_title }}_

Your shift starts on {{ job_data.start_date | abbr_date_string }} at: {{ job_data.start_date | local_time_string }}
and ends at {{ job_data.end_date | local_time_string }}.

Location: {{job_data.job_loc_name}} 
{% if job_data.job_loc_w3w %}
[Map](http://what3words.com/{{ job_data.job_loc_w3w}})
{% endif %}
{% endfor %}

{% if ical %}The attached file will add (or update) your shifts on your calendar. (Usually you can tap or double click to open it.){% endif %}

{% else %}
Hummm... something when wrong... there are no jobs listed.

{% endif %}