# -*- coding: utf-8 -*-
# from django.test import TestCase
# from __future__ import unicode_literals


# Create your tests here.
import calendar
import datetime
import re
import MySQLdb
 
 
print (datetime.date.today().replace(day=1))
 
 
db = MySQLdb.Connect(host = '127.0.0.1', port = 3306, db = 'Deployment', user = 'root', passwd = 'admin@123')
cursor = db.cursor()
tablename = 'report_datesofmonth'
# 
cursor.execute("Truncate table "+tablename)
db.commit()

def insert(date):
    print ("Insert into "+tablename+" (weekday) values ('%s')" % (date))
    cursor.execute("Insert into "+tablename+" (weekday) values ('%s')" % (date))
    db.commit()


# for day in calendar.monthcalendar(2018, 10):
#     print day
def weekdays(yr,mnt):
    print(yr,mnt)
    for day in calendar.monthcalendar(int(yr), int(mnt)):
        if day[0] != 0:
            if len(str(day[0])) == 1:
                day[0]= "0"+str(day[0])
            insert(str(yr)+'-'+str(mnt)+'-'+str(day[0]))
        if day[1] != 0:
            if len(str(day[1])) == 1:
                day[1]= "0"+str(day[1])
            insert(str(yr)+'-'+str(mnt)+'-'+str(day[1]))
        if day[2]!= 0:
            if len(str(day[2])) == 1:
                day[2]= "0"+str(day[2])
            insert(str(yr)+'-'+str(mnt)+'-'+str(day[2]))
        if day[3] != 0:
            if len(str(day[3])) == 1:
                day[3]= "0"+str(day[3])
            insert(str(yr)+'-'+str(mnt)+'-'+str(day[3]))
        if day[4] != 0:
            if len(str(day[4])) == 1:
                day[4]= "0"+str(day[4])
            insert(str(yr)+'-'+str(mnt)+'-'+str(day[4]))


today = datetime.date.today()
first = today.replace(day=1)
lastMonth = first - datetime.timedelta(days=1)
mnt = lastMonth.strftime("%m")
yr = lastMonth.strftime("%Y")
print (mnt,yr)
weekdays(yr,mnt)

yr  = datetime.datetime.now().year
mnt = datetime.datetime.now().month
weekdays(yr,mnt)
