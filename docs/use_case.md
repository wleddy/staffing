# "Staffing" Use Case

_Modified July 11, 2019_

## Overview

The "Staffing" web application is designed to help small organizations manage event staffing for volunteers and employees.

It is an open source project and the source code is available to anyone interested at [github.com/wleddy/staffing/](http://github.com/wleddy/staffing/).

**A note about this document:** *Some of what is written here is asperational at the time of this writing. Hopefully it will
be implemented later unless we decide that it was a bad idea or too much work and we just blow it off.*

### The Signup Process

In as much as the whole point of this app is to allow people to signup to work shifts (as volunteers or staff) I should
probably take some space to talk about the steps.

1. A user arrives at the home page of the app and they will see a list of upcoming jobs. Assuming they are not yet signed
in to their account, the only jobs shown will be those that don't require any particular skills. Mostly these will be 
jobs for volunteers.

2. Clicking a signup link will prompt the user to log in or create an account if they don't already have one.

3. Once logged in, the user has the option to sign up for a job. If the user has been given credit for additional "skills"
by a site administrator additional jobs may be listed where the jobs required skills match those of the user.

4. When the user finds a job they want to do, they can click the "Signup" button and then indicate how many slots they 
want to fill for that job. Usually they will sign up for just on slot, but they may be signing up for themself and a 
family member, for example. This all assumes that there is more than one unfilled slot open for the job.

5. After sign up the user will receive an email thanking them for signing up and providing the job details and a file
attachment that will add the event to their computer's calendar if they like.

6. A few days before the users' shifts are scheduled, they will each receive another email as a reminder.

## How the data is organized

The database used to drive the system is organized into the following major tables.

### Events

The central element of the system are the Events. The Event record contains information that describes the work that will
be done at the event, the date of the event (an event may not span multiple days, make more events for that), and other
information. There will always need to be one or more "Jobs" associated to an event. The Jobs are what people are actually
signing up for.

An Event may occur at one Location or each Job may specify a different location but a specific location is not required.

[More details.](/docs/events.md)

### Activities

All Events are organized within "Activities". An Activity record provides a way to organize a set of events that have 
the same purpose. 

For example, an Activity like "Bake Sale" might take place several times during the year, or even over the course of a few
years. Each "Event" associated with the Activity happens on a specific date. The Activity record provides a way to 
keep the Bake Sale events organized. 

Activities don't have a date as part of their
data domain. Activities should be thought of a things that tend to repeat on a yearly or other basis. The dates and times of 
are defined by in the Event records.

[More details.](/docs/activities.md)

### Jobs

A Job record represents something that you need someone to do in order to fulfill the purpose of the Event you are planning.

A Job record has a start and end time and may specify that you need one or more people to perform this job. You will
also specify the skills that are required to perform the job. For the most part the skills will differentiate those
jobs that can be performed by volunteers and those that are reserved for paid staff.

[More Details.](/docs/jobs.md)

### Locations

The physical location of the Event or Job and is used to provide mapping features to staff and volunteers. The jobs
associated with an event may all take place at the same location or they may each be different.

An Event need not occur at a specific location (such as work from home). In such as case there is no need 
to associate a location with an Event.

[More Details.](/docs/locations.md)

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