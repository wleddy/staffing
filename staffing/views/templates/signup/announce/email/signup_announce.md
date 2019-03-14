## Thank you for helping us with {{ job_data.event_title }}!

Your assignment is to help with {{ job_data.job_title }}.

Your shift starts on {{ job_data.start_date | abbr_date_string }} at: {{ job_data.start_date | local_time_string }}
and ends at {{ job_data.end_date | local_time_string }}.

{{ description }}

If you have questions about your shift please [contact us](http://{{config.HOST_NAME}}{{ url_for('www.contact')}})

{% if ical %}The attached file will add your shift to your calendar. (Usually you can tap or double click to open it.){% endif %}
