# Staffing App Use Case

## Overview

A proposed web application to help manage employee and volunteer staffing for SABA events.

### Events

The central element of the system are the Events. Strangely, perhaps, Events don't have a date as part of their
data domain. In our experience events tend to repeat on a yearly or other basis. The dates and times of an Event 
are defined by Spots.

An Event must occur in only one Location.


### Spots

A Spot is a record of what is required to fulfill a task that is part of an event. A Spot associated with an Event
has the following attributes:

* A date for the spot
* Start and end times for the spot
* The skills required of staff or volunteer
* The number of people requested for the spot at this skill level

### Locations

The physical location of the Event. Used to provide mapping features to staff and volunteers.

## Events

### Create / Edit Event
1. login
2. Select Event or make new
3. Specify Location from Location list
4. Upload Image if desired
5. Update general event description
6. Specify Event manager contact info

### Create / Edit Spots
 1. From Event record Select Spot or create new
 2. Provide Title
 3. Provide Description of task
 4. Provide Date (one day only per spot)
 5. Provide Start and End times
 6. Specify skills (user roles) required. May be a comma separated list of user roles. 
 Leave roles blank to allow volunteers to sign up for spots.
 7. Specify maximum number of people requested.

> Repeat for all Spots for this event

### Announce Spots

#### Staff Announcements

From Event page, Click "Announce this event to Staff"  
Text and/or emails will be sent to all staff with required skills.  

Weekly announcements will be automatically sent to all staff with 1 month of upcoming Spots.

#### Volunteer Announcements

Automated announcements will be sent to volunteers who have opted in for text and/or email announcements 
with 1 month of upcoming Spots.

## Signup

 From publicly accessable web page, a visitor may:

1. Sign in if desired. Staff must sign in to see non-volunteer events and spots.  
1. Select future Event from a list 
1. Select a volunteer spot from list of spots for Event
1. Sign in with email address (if not signed in)  
1. Users with passwords set will be required to enter password.
  *  If not known user collect info and create account
1. Acknowledge signup and send email with iCalendar event
1. Return visitor to spots list

## Reminders

Two days before spot, send email and/or text to volunteers (who opt in) and staff.

## Attendance

One day after event, send email and/or text to volunteers (who opt in) and staff.

### Staff Response
Staff will be asked to provide the hours they worked for each spot. They may also report any issues or
comments about the shift.

### Volunteer Response
The volunteer response is primarily a Thank You and a chance for them to report any issues or comments.

> Responses will update attendance status automatically. 

### Manager Attendance Updates

The managers will have access to Attendance records from the web site.

1. Sign in as manager.
1. Select "Manage Attendance"
1. Select Event and Spot
1. Select user record and update attendance info.

> Repeat as needed.

Managers may export an attendance report suitable to import into a spreadsheet

1. Sign in as manager
1. Select "Attendance Report"
1. Select Events to report
1. 'csv' report file is downloaded to user.