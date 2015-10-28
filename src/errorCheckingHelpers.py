'''
Created on 6 Aug 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''

from datetime import datetime
from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename

def getDateTime(eventLine, dateIndex, timeIndex):
    '''
    Given a list of strings (eventLine) with a yyyy-mm-dd date at [dateIndex] and the hh:mm:ss time at [timeIndex].
    Returns a datetime object with the date and time from eventLine.
    '''
    joinedTime = ' '.join([eventLine[dateIndex],eventLine[timeIndex]]) ##Result should be string 'yyyy-mm-dd hh:mm:ss'
    return datetime.strptime(joinedTime, '%Y-%m-%d %H:%M:%S')

def sameDate(eventLine1, eventLine2):
    '''
    Parameters are lists of strings, presumed to be lines of data, split and stripped.
        All that really matters, though, is [2] of both parameters is a yyyy-mm-dd date.
        
    Checks if the date in both lines is the same.
    
    Returns TRUE or FALSE.
    '''
    date1 = datetime.strptime(eventLine1[2],'%Y-%m-%d')
    date2 = datetime.strptime(eventLine2[2],'%Y-%m-%d')
    return date1 == date2

def duringFocal (eventLine, focalEndTime):
    '''
    Checks if the day/time in eventLine is before the focalEndTime.
    eventLine is a list of strings. The date is at eventLine[2], the time is at eventLine[3].
    focalEndTime is a datetime, not just a time.
    Returns TRUE or FALSE.
    '''
    eventDayTime = ' '.join(eventLine[2:4])
    eventDateTime = datetime.strptime(eventDayTime, '%Y-%m-%d %H:%M:%S')
    return eventDateTime < focalEndTime


    
    