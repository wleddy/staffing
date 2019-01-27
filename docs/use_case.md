# "Activities and Tasks" Use Case

_Modified Jan. 20, 2019_

## Overview

A proposed web application to help manage employee and volunteer staffing for SABA activities.

### Activities

The central element of the system are the Activities. Activities don't have a date as part of their
data domain. In our experience activities tend to repeat on a yearly or other basis. The dates and times of an Activity 
are defined by [Tasks](/docs/tasks.md).

An Activity may only occur at one Location though there need not be a location specified.

[More details.](/docs/activities.md)

### Tasks

A Task is a record of what is required to fulfill a task that is part of an activity.

[More Details.](/docs/tasks.md)

### Locations

The physical location of the Activity. Used to provide mapping features to staff and volunteers. An Activity may
not occur at a specific location (such as work from home). In such as case there is no need to associate a location
with an Activity.

## Announcements and Reminders

### Announcing Tasks

#### Staff Announcements

From Activity page, Click "Announce this activity to Staff"  
Text and/or emails will be sent to all staff with required skills.  

Weekly announcements will be automatically sent to all staff with 1 month of upcoming Tasks.

#### Volunteer Announcements

Automated announcements will be sent to volunteers who have opted in for text and/or email announcements 
with 1 month of upcoming Tasks.

## Signup

From publicly accessable web page, a visitor may:

1. Sign in if desired. Staff must sign in to see non-volunteer activities and tasks.  
1. Select future Activity from a list 
1. Select a volunteer task from list of tasks for Activity
1. Sign in with email address (if not signed in)  
1. Users with passwords set will be required to enter password.
  *  If not a registered user collect info and create account
1. Acknowledge signup and send email with iCalendar activity
1. Return visitor to tasks list

### Reminders

Two days before a task, an email and/or text will be automatically sent to volunteers (who opt in) and staff.

## Attendance and Thank Yous

Following an Activity the system will automatically contact the participants to thank volunteers and ask staff
to confirm their hours.

[More Details.](/docs/attendance.md)

### Manager Attendance Updates

The managers will have access to Attendance records from the web site.

1. Sign in as manager.
1. Select "Manage Attendance"
1. Select Activity and Task
1. Select user record and update attendance info.

> Repeat as needed.

Managers may export an attendance report suitable to import into a spreadsheet

1. Sign in to an manager's account
1. Select "Attendance Report"
1. Select Activities to report
1. 'csv' report file is downloaded to user. The report may then be imported into a spreadsheet program such
as Excel for additional analysis.

## Staff and Volunteer signup

The system will provide an easy to use interface for staff and the general public to discover and 
sign up for SABA Activities. 

[More Details](/docs/signups.md)

## Reports

The system will provide viewable and downloadable reports. [More detail.](/docs/reports.md)