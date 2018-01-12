import pyodbc
import json
import requests
import os
import sys
import smtplib
from datetime import datetime, date
import datetime
import time
from email.mime.text import MIMEText
from StringIO import StringIO

def sendEmail(fromm, to, subject, message):
    today = str(time.strftime("%m-%d-%y"))
    try:
        smtpObj = smtplib.SMTP('10.10.2.247')
        smtpObj.set_debuglevel(1)
        msg = MIMEText(message)
        sender = fromm
        receivers = to
        msg['Subject'] = "Stale Crash Events | " + today
        msg['From'] = sender
        smtpObj.sendmail(sender, receivers, msg.as_string())

        print "Successfully sent email: {}".format(subject)
    except Exception, e:
        print e
        print "Error: unable to send email"

        
server = '10.0.16.5'
db =''
user =''
password =''

# VARIABLES
eventNumber = 0
emailBody = ''

# CONNECT TO THE SERVER VIA THE ABOVE CREDENTIALS
conn = pyodbc.connect("DRIVER={/usr/local/lib/libmsodbcsql.13.dylib};SERVER=" + server + ';DATABASE=' + db +';UID=' + user + ';PWD=' + password)
cursor = conn.cursor()

# GET CRASHES OLDER THAN 8 HOURS VIA SQL
cursor.execute('SELECT sub.* FROM(SELECT situation_id, update_number, update_timestamp, situation_update_json FROM (SELECT *, maxnum = MAX(update_number) OVER (PARTITION BY situation_id) FROM [SACARS].[dbo].[evt_Situations]) as s WHERE update_number = maxnum) sub WHERE situation_update_json LIKE \'%"headline":{\"category\":%\' AND update_timestamp < DATEADD(hh, -11, GETDATE()) AND situation_update_json NOT LIKE \'%DELETE%\' AND situation_update_json NOT LIKE \'%ENDED%\'')

# FETCH ALL DATA FROM THE SQL QUERY AND PRINT IT
allEventsJson = cursor.fetchall()
numberOfEvents = len(allEventsJson)
print '\n' + 'Events In The Database: ' + str(numberOfEvents)

crashEventIDs = []
for event in allEventsJson:
        crashEventIDs.append(event[0])

for event in allEventsJson:
    detailsJson = allEventsJson[eventNumber][3]
    detailsJsonData = json.loads(detailsJson)
    eventEpochTime = detailsJsonData['updateTimestamp']['time']
    updateTime = datetime.datetime.fromtimestamp(eventEpochTime/1000)
    currentTime = datetime.datetime.utcnow()

    emailBody = emailBody + '\n' + 'Event ID: ' + allEventsJson[0][0]
    emailBody = emailBody + '\n' + ">Event's Age: " + str((currentTime - updateTime))
    emailBody = emailBody + '\n' + '>Last Updated: ' + str(updateTime) + '\n'

    eventNumber+=1

print 'The number of crash items in need of review: ' + str(len(crashEventIDs))

# SEND EMAIL
if numberOfEvents > 0:
        emailString = 'Hello,' + '\n' + '\n' + 'The following Crash Events in Sacog Staging are older than 8 hours: ' + '\n'
        # for item in crashEventIDs:
        #         emailString = emailString + str(item) + '\n'
        emailString = emailString + emailBody
        emailString = emailString + '\n' + '\n' + 'Best regards,' + '\n' + '\n' + 'Castle Rock QA Robot'

        Message = emailString
        Subject = 'Test Email'
        From = 'ryan.kavanaugh@crc-corp.com'
        To = ['ryan.kavanaugh@crc-corp.com', 'lauren.jenkins@crc-corp.com']  # 'mary.crowe@crc-corp.com',
        print emailString
        sendEmail(From, To, Subject, Message)
