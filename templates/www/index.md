# SABA Staff and Volunteer Signups

{% if not g.user %}
SABA staff can use this site to manage Events.

You will need to [log in]({{url_for('login.login')}}) to access your controls.

If you actually came here to sign up for a shift as a staff member or a volunteer, you can 
[sign up here!](http://signup.{{config.SERVER_NAME}})

If you have questions, please feel free to [contact us.]({{url_for('www.contact')}})
{% else %}
## You're signed in!

At some point in the future, your "Dashboard" of controls will appear here. For now, you'll just have to dream about it.

In the mean time, check out the menu to the right (or the "Hamburger" above if your on your phone). You may have access
to Activity and task records there.

{% endif %}