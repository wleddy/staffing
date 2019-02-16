## Thank you for helping us with {{ job_data.event_title }}!

Your assignment is to help with {{ job_data.title }}.

Your shift starts on {{ job_data.start_date | abbr_date_string }} at: {{ job_data.start_date | local_time_string }}
and ends at {{ job_data.end_date | local_time_string }}.

If you have questions about your shift please [contact us]({{ url_for('www.contact')}})

*location:*

{{ job_data.job_loc_name }}

{{ job_data.job_loc_street_address }}, {{ job_data.job_loc_city }} {{ job_data.job_loc_state | upper }}

{% if map_url %}
Map: {{ map_url }}
{% endif %}

{% if ical %}
The attached file will add your shift to your calendar. (Usually you can tap or double click to open it.)
{% endif %}