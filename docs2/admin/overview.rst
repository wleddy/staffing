==================================
Overview
==================================

The **Staffing** system is a web based application designed primarily to allow non-profits
and other organizations that use volunteers and/or paid staff to get things done.

It includes an automatically created `Calendar <calendar.html>`_ so that visitors to your web site
can see what you're up to.

At a high level the system is organized around the following hierarchy:

* `Activities <activities.html>`_ help you organize what you do and contain...
    * `Events <events.html>`_ that happen at a specific date and time and may (or my not) contain...
    
    (If all you want to do is add an item to the `calendar <calendar.html>`_ then you are done.)
        * `Jobs <jobs.html>`_ which are the things you need people to do during the event.
        
        Jobs have a start and end time (shifts) and you will indicate how many people you need to do the
        job during that time.
        
        
Basic Steps
***********

On a practical level, you need to create at least one *Activity* record, then create an *Event* record to go with it
and finally, if needed, create one or more *Job* records for the thing that needs to be done. 

The links above will take you to detailed instructions on how to accomplish each of these tasks

About Staffing
**************

The Staffing application is an open source Python based project that is free for anyone to use. The source code 
is available at `<http://github.com/wleddy/staffing/>`_.

It was initially created for the Sacramento Bicycle Advocates as a way to organize and publicize events in the 
Sacramento area. 