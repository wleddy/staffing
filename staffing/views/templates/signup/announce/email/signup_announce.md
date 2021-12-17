{# job_data_list should only contain one item #}
{% if job_data_list %}{% set job_data = job_data_list[0] %}
{% from '_staffing_helper_macros.html' import directions_snippet %}
                
## Thank you for helping us with {{ job_data.activity_title }}!

Your assignment is to help with {{ job_data.job_title }}.

Your assignment Date: {{ job_data.start_date | abbr_date_string }}

Your shift begins at {{ job_data.start_date | local_time_string }}
and ends at {{ job_data.end_date | local_time_string }}.


{{ description | safe }}

{% include "announce/email/addendum.md" %}

{{ directions_snippet(job_data) | safe }}

If you have questions about your shift or you're unable to make it for some reason please 
[Contact the Event Manager](http://{{config.HOST_NAME}}{{ url_for('signup.contact_event_manager')}}{{ job_data.job_id | default('',True) }}/).

{% if ical %}The attached file will add your shift to your calendar. (Usually you can tap or double click to open it.){% endif %}
{% else %}

Humm... Something is wrong. There are no jobs to list...

Please [contact us](http://{{site_config.HOST_NAME}}{{ url_for('signup.contact')}}) so we can look into it.

_Thanks_

{% endif %}
