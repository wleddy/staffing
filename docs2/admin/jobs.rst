===================================
How to manage Job records
===================================
(Jump to :ref:`job_instructions`)

Most Events will require one or more people to do one or more **Jobs**. It's possible to have an Event with
no jobs if, for example you only want the event to appear on the calendar. 
When staff and volunteers are using the system sign up, they are actually signing up for a Job.

Each Job record will have a start time and end time and will request one or more people for the job.

The dates and times for each job may be different from the date and times of the event to which the
job is associated.


.. _job_instructions:

How to Create or Edit a Job record
**************************************

As an Admin or Event coordinator you will be able to `create and edit Jobs <#create-or-open-a-job-record>`_,
`assign users <#assign-a-user>`_ to work a Job and `remove a user from a job <#assign-a-user>`_.

Create or Open a Job Record
^^^^^^^^^^^^^^^^^^^^^^^^^^^

From an `Event <events.html>`_ record...

    .. image:: images/jobs/open.png
        :width: 500px
        
    #. To create a new job, click the :guilabel:`New Job` button.
    #. Or... click the :guilabel:`Edit` button to open an existing Job record.
    #. Or... click the :guilabel:`Assign` button to assign users to work the job.
    
Edit a Job Record
^^^^^^^^^^^^^^^^^

    .. image:: images/jobs/detail.png
        :width: 500px
        
    #. Enter a Job title
    #. Create a description of the job
        This is a public facing description of what the job is about. 
        
        This is a good opportunity to give folks a reason to sign up for the job. 
        
        The description may use `Markdown <https://www.markdownguide.org/basic-syntax>`_ syntax to create a rich presentation when viewed by visitors. (Or you can just type something.)
    #. Select the Skills Required.
        Select one or more `Roles <roles.html>`_ that a user must have associated with their profile in order to sign up for
        this Job.
        
        In order for this job to be listed in the sign up page, a user must be logged in and they must have at lease one
        of the required roles. 
        
        .. note:: Roles are hierarchical based on the role's "Rank" so that a user with a role that has a higher rank than the rank of
          any of the roles selected will also be elegible to sign up for the job.
          
    #. Enter the start and end times for the job.
    #. Enter the number of people you need for this job.
        This will limit the number of people who can sign up.
    #. Set the location for the job.
        Set this if the job location is not the same as the default location for the event.

Assign a User
^^^^^^^^^^^^^^^
As an Administrator or the Event coordinator, you have the ability to `assign a job to a user <assign_users_to_jobs.html>`_ to work the event.

Emails and Reminders
********************

When a user signs up for a shift or an administrator assigns them a shift, the user will receive an email with the shift details.

In addition, a few days before their shift, the user will receive another similar email as a reminder. The default is that the
email will be sent 2 days in advance. The System administrator can change the number of days by changing the value in the "Commitment Reminder Days" 
value in the Preferences table. This is a system wide preference that effects all future reminders.

.. note:: As mentioned before, these emails are only sent when the shift is in future so that if you assign a user to a past shift
    in order to create an Assignment record, no emails will be sent to the user.


Reminder Trigger
^^^^^^^^^^^^^^^^

The sending of reminder emails is triggered by calling a special web address: `https://<web site name>/process_notifications/ </process_notifications/>`_

The notification web address requires that you be logged in but does not require any special privileges.



