[Return to Index](/docs/use_case.md)

# Jobs

A Job record describes what is needed to fulfill part of an Event. A Job has the following attributes:

* A date
* Start and end times
* The skills required of staff or volunteer to perform the job
* The number of people requested for the job at the given skill level
* An optional location

A person signs up for a "Position" in the Job. There may be multiple Positions for a Job. 

For example if you want 2 volunteers for a Job that runs from 4 o'clock to 6 o'clock you would set 
the "Number of People Requested" to 2 for that job. 

If you want more volunteers for a 6 to 8 time period, you need to create a new Job for those Positions.

Likewise, if you need a "Valet Lead" person to oversee a "Bike Valet" Event, you will need to create
another Job and assign an appropriate Skill level to the Job.

## Create / Edit Jobs
 1. From Event record select a Job or create new
 2. Provide Title
 3. Provide Description of job.
    The description may use [*Markdown*](https://www.markdownguide.org/basic-syntax) syntax to create a rich
    presentation when viewed by visitors.
 4. Provide Date (one day only per job)
 5. Provide Start and End times
 6. Specify skills (user roles) required for the Job. At least one skill level is required.
 7. Specify maximum number of people requested.
 8. Select a location for this job if desired.  
 If the Event associated has a location, it will be used as the location for this job unless you specify
 one here.

> Repeat for all Jobs for this Event

## Skills

The list of skills available for Jobs is based on the the User Roles records. The site administrator will
need to create Roles that represent the jobs that you need done. The following is my current proposal for
some useful skills.

**System Level Roles**
* super _Level:_ 1000
* admin _Level:_ 900

**Event Level Roles**
* site manager _Level:_ 100
    Similar access as admin
* event manager _Level:_ 90
    May manage any event

**Staff Members**
* <event lead> _Level:_ 80 ~ 70
    Actual name skill to describe the role
    Create additional event lead level roles with differing access levels as needed
* <event staff> _Level:_ 69 ~ 50
    Staff members with specific qualifications but not usually supervised by a manager or lead

**Volunteers**
* <event volunteer> _Level:_ 49 ~ 20
    A volunteer with specific qualifications
* volunteer _Level:_ 10
    A general volunteer with no specific training




[Return to Index](/docs/use_case.md)
