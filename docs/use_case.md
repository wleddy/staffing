# "Events and Jobs" Use Case

_Modified Jan. 27, 2019_

## Overview

A proposed web application to help manage employee and volunteer staffing for SABA events.

### Events

The central element of the system are the Events. Events don't have a date as part of their
data domain. In our experience events tend to repeat on a yearly or other basis. The dates and times of an Event 
are defined by [Jobs](/docs/jobs.md).

An Event may occur at one Location or each Job may specify a different location. A specific location is not requried.

[More details.](/docs/events.md)

### Jobs

A Job is a record of what is required to fulfill a job that is part of an event.

[More Details.](/docs/jobs.md)

### Locations

The physical location of the Event. Used to provide mapping features to staff and volunteers. An Event may
not occur at a specific location (such as work from home). In such as case there is no need to associate a location
with an Event.

## Announcements and Reminders

### Announcing Jobs

#### Staff Announcements

From Event page, Click "Announce this event to Staff"  
Text and/or emails will be sent to all staff with required skills.  

Weekly announcements will be automatically sent to all staff with 1 month of upcoming Jobs.

#### Volunteer Announcements

Automated announcements will be sent to volunteers who have opted in for text and/or email announcements 
with 1 month of upcoming Jobs.

## Staff and Volunteer signup

The system will provide an easy to use interface for staff and the general public to discover and 
sign up for SABA Events. 

[More Details](/docs/signups.md)

### Reminders

Two days before a job, an email and/or text will be automatically sent to volunteers (who opt in) and staff.

## Attendance and Thank Yous

Following an Event the system will automatically contact the participants to thank volunteers and ask staff
to confirm their hours.

[More Details.](/docs/attendance.md)

## Reports

The system will provide viewable and downloadable reports. [More detail.](/docs/reports.md)