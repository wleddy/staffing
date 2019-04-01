## Your 2 Day Reminder from {{ site_config.site_name }}

You have the following Job commitments coming up in the next couple days.

If you are unable to make it to any of the events, please contact {{ site_config.contact_name} at {{ site_config.contat_email_addr }}
so we can arrange to fill your spot.

{% if job_data %}
{% for job in job_data %}

{% endfor %}

{% if ical %}The attached file will add your shift to your calendar. (Usually you can tap or double click to open it.){% endif %}

{% else %}
Hummm... something when wrong... there are no jobs listed.

{% endif %}