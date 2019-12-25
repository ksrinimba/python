"""
K.Srinivas, 29-Aug-2019
Project: Emp Dash - FingerPrint Data only
Description: This contains the views for displaying emp finger-print data. The views are
generic for displaying weekly, monthly and quarterly aggregates with a link to raw data.

TODO: 
=> Add a check if ZERO entries in the data. This is an unrealistic scenario.
"""
import logging

from flask import Flask, url_for, send_from_directory, render_template, redirect, request, flash
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import datetime
import os
import datetime as dt
from bcsutils import getDIMFromDate, getEmpBCSOrgFromEmailId 
from realapp import app, db
from processdata import *
from bcsauthinterface import empDashcheckauth
from attendenceutils import *
from genempreports import updateAllEmpImpactMetrics
from batchjobs import updateYearlyAttendenceDataForAll, generateAllImpactReports
from empreportutils import getStartAndEndDIMs, getDateDimList

@app.route('/empdash/showimpactdata', methods=('GET', 'POST'))
@app.route('/empdash/showimpactdata/<int:dateDim>', methods=('GET', 'POST'))
@login_required
def showImpactData(dateDim = 0) : 
    empEmail = current_user.username.lower()
    # ext_id = 1211
    #Get Ext Id from e-mail
    bcsOrg = getEmpBCSOrgFromEmailId(empEmail, useIsValid = False)
    if not bcsOrg :
        return render_template("empdash/message.html", message = "Your Data is not linked in BCSPROJ. Please contact PMO team")

    ext_id = bcsOrg.external_id
    if not dateDim :
        dateDim = getDIMFromDate(dt.date.today()) - 1 # Yesterday
    recs = getRecordsByEmployeeAndDate(ext_id,dateDim)
    dateFromDIM = getDateFromDIM(dateDim)
        
    title = "Biometric Data for " + dateFromDIM.strftime('%d-%m-%Y')

    (totalTimeSpentAtDesk, totalTimeAtPantry, totalTimeSpentInOffice, firstOfficeEntry, lastOfficeExit, comments) = empSummaryTime(recs)

    makeItRed = False
    if totalTimeSpentAtDesk < 450 :
        makeItRed = True
    return render_template("empdash/empday.html", itemSet = recs, ttsd = getTimeStringFromMinutes(totalTimeSpentAtDesk), \
        ttap = getTimeStringFromMinutes(totalTimeAtPantry), ttso = getTimeStringFromMinutes(totalTimeSpentInOffice), \
        st = getTimeStringFromMinutes(firstOfficeEntry), et = getTimeStringFromMinutes(lastOfficeExit), 
        message = "" , mesgRED=makeItRed, title = title )

@app.route('/empdash/showimpactsummary', methods=('GET', 'POST'))
@login_required
def showImpactSummary() : 
    empEmail = current_user.username.lower()
    (startDateDim, endDateDim) = getDimListByRange()
    title = "Attendence for the entire year" 
    return  showImpactSummaryByRange(empEmail,title,startDateDim, endDateDim)


@app.route('/empdash/showimpactsummaryforweek/<int:weeknum>', methods=('GET', 'POST'))
@login_required
def showImpactSummaryForWeek(weeknum=0) : 
    empEmail = current_user.username.lower()
    (startDateDim, endDateDim) = getDimListByRange(quarter = None, month=None, week = weeknum)
    title = "Attendence Summary for week number: " + str(weeknum) 
    return  showImpactSummaryByRange(empEmail,title,startDateDim, endDateDim)

@app.route('/empdash/showimpactsummaryformonth/<int:month>', methods=('GET', 'POST'))
@login_required
def showImpactSummaryForMonth(month=0) : 
    empEmail = current_user.username.lower()
    (startDateDim, endDateDim) = getDimListByRange(quarter = None, month=month, week = None)
    title = "Attendence Summary for Month: " + str(month) 
    return  showImpactSummaryByRange(empEmail,title,startDateDim, endDateDim)

@app.route('/empdash/showimpactsummaryforquarter/<int:quarter>', methods=('GET', 'POST'))
@login_required
def showImpactSummaryForquarter(quarter=0) : 
    empEmail = current_user.username.lower()
    (startDateDim, endDateDim) = getDimListByRange(quarter = quarter, month=None, week = None)
    title = "Attendence Summary for Quarter: Q" + str(quarter) 
    return  showImpactSummaryByRange(empEmail,title,startDateDim, endDateDim)

def getDimListByRange(quarter = None, month=None, week = None) :
    date = dt.date.today()
    year = date.year

    if week :
        return getStartAndEndDIMs(year, False ,False, week)
    if month:
        return getStartAndEndDIMs(year, month ,False, None)
    if quarter:
        return getStartAndEndDIMs(year, None ,quarter, None)
    today= dt.date.today()
    endDateDim = getDIMFromDate(today)
    startDateDim = getDIMFromDate(dt.date(year=today.year, month=1, day=1))
    return (startDateDim, endDateDim)

def showImpactSummaryByRange(empEmail,title,startDateDim, endDateDim) : 
    empEmail = current_user.username.lower()
    bcsOrg = getEmpBCSOrgFromEmailId(empEmail, useIsValid = False)
    if not bcsOrg :
        return render_template("empdash/message.html", message = "Your Data is not linked in BCSPROJ. Please contact PMO team")

    ext_id = bcsOrg.external_id
    attendRecList = getEmpAttendenceRecords( bcsOrg.external_id, startDateDim,endDateDim)
    augmentEmpAttendence(attendRecList)
    return render_template("empdash/empsummary.html", itemSet = attendRecList, message="", title = title )

#Method to impersonate another employee, used for testing and support
@app.route('/impersonate/<emailId>', methods = ['GET'])
@login_required
def impersonate(emailId):
    from logindomain import impersonateEmployee
    from hrmsdomain import getEmployeebyId, getEmpIdByEmail
    loginAs = emailId
    if not current_user.is_admin :
        return redirect(url_for("unauthorized"))
    emp = getEmpIdByEmail(emailId)
    if not emp : #Not found, see if you can find by ID (ID given instead of email)
        emp = getEmployeebyId(emailId)
        if emp : #Cannot be found
            loginAs = emp.OFFICE_EMAIL_ID
        else :
            return render_template("message.html", message="Employee could not be found")
            
    impersonateEmployee(loginAs, current_user) 
    return redirect(url_for("home"))


###############################################################################################
### FOR TESTING ONLY
###############################################################################################

@app.route('/empdash/sendimpactdataemail/<int:id>', methods=('GET', ))
@login_required
def sendEmployeeImpactDataEmail(id = 0) : 
    empEmail = current_user.username.lower()
    if not empDashcheckauth(empEmail) :
        return redirect(url_for('unauthorized'))
    #For sending e-mail to one person
    numDays = 1
    if id :
        # ext_id=id=1341 # Ukkala
        # ext_id=id=1211 # Kambhampati
        # dateDim = getDIMFromDate(dt.date(day=22, month=8, year=2019)) - 1 # Yesterday
        dateDim = getDIMFromDate(dt.date.today()) - numDays # Yesterday
        # print("DateDim=" + str(dateDim))
        sendEmployeeImpactEmail(id, dateDim)
        message = "Email for employee with external ID %s has been sent" % str(id)
    else :
        message = "Email for ALL employees has been queued. Wait for 10 min before checking"
        sendEmployeeImpactDataEmailForAll()
    return render_template("empdash/message.html", message = message)

#Special method for PMO to update the reports right after loading the data.
#Its updated for previous month by default
@app.route('/empdash/updateattendencebymonth/<int:month>', methods=('GET', ))
@app.route('/empdash/updateattendencebymonth', methods=('GET', ))
@login_required
def manualReportUpdate(month = -1) : 
    empEmail = current_user.username.lower()
    if not empDashcheckauth(empEmail) :
        return redirect(url_for('unauthorized'))
    date = dt.date.today()
    year = date.year
    if month < 0 : # Get previous month, and if required year
        month = date.month        
        if month == 1 :
            month = 12
            year = year -1
        else :
            month -= 1  
    (startDateDim, endDateDim) = getStartAndEndDIMs(year, monthNum=month,quarterNum=None, weekNum=None )
    updateYearlyAttendenceDataForAll(startDateDim, endDateDim)
    flash("All reports updated")
    return redirect(url_for("home"))


from notifyusers import recordNotificationRequest, sendNotification
@app.route('/empdash/testsetnotify', methods=('GET', ))
@login_required
def testdim3() : 
    recordNotificationRequest()
    return "Check DB"


from updateattendence import getRecordsByEmployeeAndDateRanage, getEmpAttendence
from processdata import empSummaryTime
@app.route('/empdash/testdim', methods=('GET', ))
@login_required
def testdim5() : 
    dateDim  = 3533
    recHash = getRecordsByEmployeeAndDateRanage(1870, dateDim, dateDim) 
    empSummaryTime(recHash[dateDim])
    # for week in range(1,40) :
    #     (startDateDim, endDateDim) = getStartAndEndDIMs(2019, monthNum=None,quarterNum=None, weekNum=week )
    #     getEmpAttendence(1211, startDateDim, endDateDim)
    # getStartAndEndDIMs(2019, monthNum=None,quarterNum=None, weekNum=1 )
    return "Check logs"
