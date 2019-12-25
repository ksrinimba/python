"""
K.Srinivas, 26-Sep-2019

Description: Reporting DB table definitions that will( be populated by overnight jobs. The following tables
envisaged: All data will be available in aggregatable values. YTD tables can be added in future if required.
a) Emp info By-week: Hours spent in office, Billable hours, Non-Compliance incidents, media-start-time, media-exit-time
b) Emp info By-month: Hours spent in office, Billable hours, Non-Compliance incidents, media-start-time, media-exit-time, utilization% 
c) Emp Info by Quarter: Hours spent in office, Billable hours, Non-Compliance incidents, media-start-time, media-exit-time, utilization%
d) Year-to-date: Hours spent in office, Billable hours, Non-Compliance incidents, media-start-time, media-exit-time, utilization%
"""


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from realapp import db
import datetime as dt
import logging


##################################################################################################
### EMPLOYEE AGGREGATES without PROJECT
##################################################################################################
class RepEmpImpactWeekly(db.Model):
    __bind_key__ = 'empdash'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    externalId = db.Column(db.BigInteger)
    #Facts
    medianEntryTimeHour = db.Column(db.Integer, nullable=False, default = 0)
    medianEntryTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)

    medianExitTimeHour = db.Column(db.Integer, nullable=False, default = 0)
    medianExitTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)

    inOfficeNumHours =  db.Column(db.Integer, nullable=False, default = 0)
    inOfficeNumMinutes = db.Column(db.Integer, nullable=False, default = 0)

    inPantryNumHours =  db.Column(db.Integer, nullable=False, default = 0)
    inPantryNumMinutes = db.Column(db.Integer, nullable=False, default = 0)

    atDeskNumHours =  db.Column(db.Integer, nullable=False, default = 0)
    atDeskNumMinutes = db.Column(db.Integer, nullable=False, default = 0)

    numNonCompliance = db.Column(db.Integer, nullable=False, default = 0)

    numWorkingDays = db.Column(db.Integer)     # Additive
    #Dimensions
    year = db.Column(db.Integer)
    week = db.Column(db.Integer)
    #Emp-Details
    empBCSName = db.Column(db.String(80)) 
    hrmsDC = db.Column(db.String(50))
    careerLevel = db.Column(db.String(50))
    hrmsEmpStatus = db.Column(db.String(80))
    skillCat = db.Column(db.String(50))
    skillGroup1 = db.Column(db.String(50))
    skillGroup2 = db.Column(db.String(50)) 


class RepEmpImpactMonthly(db.Model):
    __bind_key__ = 'empdash'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    externalId = db.Column(db.BigInteger)
    #Facts
    medianEntryTimeHour = db.Column(db.Integer, nullable=False, default = 0)
    medianEntryTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)

    medianExitTimeHour = db.Column(db.Integer, nullable=False, default = 0)
    medianExitTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)

    inOfficeNumHours =  db.Column(db.Integer, nullable=False, default = 0)
    inOfficeNumMinutes = db.Column(db.Integer, nullable=False, default = 0)

    inPantryNumHours =  db.Column(db.Integer, nullable=False, default = 0)
    inPantryNumMinutes = db.Column(db.Integer, nullable=False, default = 0)

    atDeskNumHours =  db.Column(db.Integer, nullable=False, default = 0)
    atDeskNumMinutes = db.Column(db.Integer, nullable=False, default = 0)

    numNonCompliance = db.Column(db.Integer, nullable=False, default = 0)

    billHours = db.Column(db.Float)         # Additive
    leaveHours = db.Column(db.Float)        # Non Additive with-in a time-window, per employee
    unbillHours = db.Column(db.Float)       # Non Additive with-in a time-window
    #Facts = Computed
    utilPercent = db.Column(db.Float)       # Non Additive 
    shadowHours = db.Column(db.Float)       # Additive 
    numHolidays = db.Column(db.Integer)     # Additive
    numWorkingDays = db.Column(db.Integer)     # Additive
    #Dimensions
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    #Emp-Details
    empBCSName = db.Column(db.String(80)) 
    hrmsDC = db.Column(db.String(50))
    careerLevel = db.Column(db.String(50))
    hrmsEmpStatus = db.Column(db.String(80))
    skillCat = db.Column(db.String(50))
    skillGroup1 = db.Column(db.String(50))
    skillGroup2 = db.Column(db.String(50)) 

class RepEmpImpactQuarterly(db.Model):
    __bind_key__ = 'empdash'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    externalId = db.Column(db.BigInteger)
    #Facts
    medianEntryTimeHour = db.Column(db.Integer, nullable=False, default = 0)
    medianEntryTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)

    medianExitTimeHour = db.Column(db.Integer, nullable=False, default = 0)
    medianExitTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)

    inOfficeNumHours =  db.Column(db.Integer, nullable=False, default = 0)
    inOfficeNumMinutes = db.Column(db.Integer, nullable=False, default = 0)

    inPantryNumHours =  db.Column(db.Integer, nullable=False, default = 0)
    inPantryNumMinutes = db.Column(db.Integer, nullable=False, default = 0)

    atDeskNumHours =  db.Column(db.Integer, nullable=False, default = 0)
    atDeskNumMinutes = db.Column(db.Integer, nullable=False, default = 0)

    numNonCompliance = db.Column(db.Integer, nullable=False, default = 0)

    billHours = db.Column(db.Float)         # Additive
    leaveHours = db.Column(db.Float)        # Non Additive with-in a time-window, per employee
    unbillHours = db.Column(db.Float)       # Non Additive with-in a time-window
    #Facts = Computed
    utilPercent = db.Column(db.Float)       # Non Additive 
    shadowHours = db.Column(db.Float)       # Additive 
    numHolidays = db.Column(db.Integer)     # Additive
    numWorkingDays = db.Column(db.Integer)     # Additive
    #Dimensions
    year = db.Column(db.Integer)
    quarter = db.Column(db.Integer)
    #Emp-Details
    empBCSName = db.Column(db.String(80)) 
    hrmsDC = db.Column(db.String(50))
    careerLevel = db.Column(db.String(50))
    hrmsEmpStatus = db.Column(db.String(80))
    skillCat = db.Column(db.String(50))
    skillGroup1 = db.Column(db.String(50))
    skillGroup2 = db.Column(db.String(50)) 

