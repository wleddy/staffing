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
`assign users <#assign-a-user>`_ to work a Job and `remove a user from a job <#remove-a-user-assignment>`_.

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
As an Administrator or the Event coordinator, you have the ability to assign users to work the event.

To start, click the :guilabel:`Assign` button from the Job list of the Event record.

    .. image:: images/jobs/assign.png
        :width: 500px
    
    #. Search for a user to assign
        Start typing the name of a user you want to assign to this job.
        
        When you find the name, click on it in the list to select it.
        
        .. note:: You can assign any user to any job you like. 
            
            You can also assign as many people to the job as you wish.
            
    #. Specify the number of "slots" you're assigning the user in case they're bringing a friend.
    #. Click the :guilabel:`Add` button to make the assignment.
        The user's name will be added to the list at the top of the form.
        
        When you add a user to the job they will receive an email with their assignment 
        info **if the job date is in the future** (`Why would I do this? <#why-assign-users-to-past-jobs>`_).
        
Remove a user assignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^
    You can also remove a user's assignment by clicking the "X" next to their name in the list at the top of the form.
    
    When you remove a user's assignment they will receive an email informing them of the change
    **if the job date is in the future** (`Why would I do this? <#why-assign-users-to-past-jobs>`_).
    
Why Assign Users to Past Jobs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When a user signs up for a job, or is assigned a job by you, a corresponding `Attendance Record <attendance.html>`_ 
is created. 

Attendance records are used to track who did what for future reference. They are also very helpful in the case of paid
staff so that you are able to pay them for their actual hours worked.

There are times when in the heat of the moment you may need to shuffle staff around to cover all the bases. The system gives
you the option to update the job assignments after the fact so that your records are accurate but without restricting
how you actually do the work.



