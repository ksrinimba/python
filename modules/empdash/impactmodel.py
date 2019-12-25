"""
K.Srinivas, 27-Sep-2019

Project: Emp Dash - Data model for impact data
EmpMap : Map employee between Bio-metric system and bcsorg table in bcsproj
EmpHit: Direct upload of the impact data
EmpAttendence : Calculated values by day that are further aggregated and stored in the 
reporting tables (defined in repimpactmodel)


KNOWN BUGs: None
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from realapp import db
import datetime as dt
import logging
from repdimmodel import DimDate

#TODO: Add employee-last working day
class EmpMap(db.Model):
    __bind_key__ = 'empdash'
    __tablename__ = 'emp_map'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    external_id = db.Column(db.BigInteger,  unique=True, nullable=True) 
    empName = db.Column(db.String(80), nullable=False ) 
    #Record is VALID flag to be added
    isValid = db.Column(db.Boolean(), default=False) # Do we have the required information?

#TODO: Add employee-last working day
class EmpHit(db.Model):
    __bind_key__ = 'empdash'
    __tablename__ = 'emp_impact'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    external_id = db.Column(db.BigInteger, default=0) 
    seqId = db.Column(db.BigInteger,  nullable=False, unique=False) 
    empNameRaw = db.Column(db.String(200), nullable=False ) 
    genTimeRaw = db.Column(db.String(80), nullable=False) # Active, Inactive, on LOA,etc.
    doorRaw = db.Column(db.String(80), nullable=False) # Active, Inactive, on LOA,etc.
    siteRaw = db.Column(db.String(80), nullable=False) # Active, Inactive, on LOA,etc.
    typeRaw = db.Column(db.String(80), nullable=False) # Biometric/card, etc
    timeMinutes = db.Column(db.Integer, nullable=False, default=0 )
    dateDim = db.Column(db.BigInteger,  nullable=False, default=0)
    door = db.Column(db.Integer,  nullable=False, default=0)
    entryExit = db.Column(db.Boolean(), default=False) # True=Entry, False = Exist


class EmpAttendence(db.Model):
    __bind_key__ = 'empdash'
    __tablename__ = 'emp_attendence'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True )
    external_id = db.Column(db.BigInteger, default=0) 
    #date
    dateDim = db.Column(db.BigInteger,  nullable=False, default = 0 ) 
    # dateDimObj = db.relationship('DimDate', primaryjoin='EmpAttendence.dateDim == DimDate.id', backref='attendenceDate')
    entryTimeHour = db.Column(db.Integer, nullable=False, default = 0)# Total MINUTES
    entryTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)# Total MINUTES
    exitTimeHour = db.Column(db.Integer, nullable=False, default = 0)# Total MINUTES
    exitTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)# Total MINUTES
    pantryTimeHour = db.Column(db.Integer, nullable=False, default = 0)# Total MINUTES
    pantryTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)# Total MINUTES
    floorTimeHour = db.Column(db.Integer, nullable=False, default = 0)# Total MINUTES
    floorTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)# Total MINUTES
    totalTimeHour = db.Column(db.Integer, nullable=False, default = 0)#  Total MINUTES 
    totalTimeMinutes = db.Column(db.Integer, nullable=False, default = 0)#  Total MINUTES 
    daytype = db.Column(db.String(2), nullable=False, default= 'N') # Normal,E
    attendenceCode = db.Column(db.String(25), nullable=False, default = "N")#  WFH, leave, Holiday-work, normal, R=Remote Sat/Sun : W, 8, 4, H, N , S,I=interviews, 8/4= Full/Half-day leave
    attendenceOK= db.Column(db.Boolean(), default=False) # True full attendence, False - fail, taking into account half-day leave
    comment = db.Column(db.String(200), nullable=False, default= "") # Allow comments from employee as explanation
