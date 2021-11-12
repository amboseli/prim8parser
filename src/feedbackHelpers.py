'''
Created on 9 Jan 2020

Functions for portraying feedback in formats that are more-familiar to
our Kenyan observers.

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''
from babaseWriteHelpers import isType
from datetime import datetime

def kenyaDateTime(strDateTime, useTime = True):
    '''
    Converts the date/time in strDateTime into a string of the format that
    our Kenyan observers are more familiar with: "ddmmmyy hh:mm:ss".
    
    strDateTime is a string showing a date (with or without a time), with the
    format, "yyyy-mm-dd hh:mm:ss".
    
    useTime is a boolean, indicating if the function should check 
    strDateTime for the time or just the date.
    
    Returns a string: the date/time in the new format. If useTime is False,
    the string only returns the date.
    '''
    thisStr = strDateTime[:]
    
    if not useTime: # Then only fetch the date
        thisStr = thisStr[:10] + ' 00:00:00'
        
        thisDate = datetime.strptime(thisStr, '%Y-%m-%d %H:%M:%S')
        return (datetime.strftime(thisDate, '%d%b%y')).upper()
    
    thisDate = datetime.strptime(thisStr, '%Y-%m-%d %H:%M:%S')
    return (datetime.strftime(thisDate, '%d%b%y %H:%M:%S')).upper()

def kenyaFixDateInLine(dataLine):
    '''
    Given dataLine--a single line from a processed prim8 data file that
    has been stripped and split--replace the 'yyyy-mm-dd' date at
    dataLine[2] with the date in the format preferred by our Kenyan
    observers.
    
    Returns the list of strings, with the format changed at [2].
    '''
    dataLine[2] = kenyaDateTime(dataLine[2], False)
    
    return dataLine

def kenyaLinesPerDay(dataLines, sampleType='', typeName = ''):
    '''
    Just like the "countLinesPerDay" function in errorCheckingHelpers, but
    this one adjusts lots of the formatting for the sake of our Kenyan
    observers.  Also adds a "typeName" parameter, allowing a more-common
    word/phrase to use in output instead of the sampleType.
    
    e.g. if sampleType = focalAbbrev, typeName might be "Focal Sample".
    '''
    # Get all possible dates from dataLines and add them to a dictionary that
    # will count lines per date.
    dateCounts = {}
    
    for line in dataLines:
        if line[2] not in dateCounts:
            dateCounts[line[2]] = 0
    
    # Condense dataLines into only those with correct sampleType.
    #
    # Do this after collecting possible dates so we can keep dates with zero lines. 
    theseLines = []
    if sampleType == '':
        theseLines = dataLines[:]
    else:
        theseLines = [line for line in dataLines if isType(line, sampleType)]
    
    # Go through data and count lines per date
    for line in theseLines:
        dateCounts[line[2]] += 1
    
    # Handle typeName, if provided.
    lineType = typeName or sampleType or 'Line'

    # Write the results
    resultInfo = []
    commentLine = lineType + 's Collected Per Day:'
    resultInfo.append(commentLine)
    
    for (date, count) in sorted(dateCounts.items(), key = lambda pair: pair[0]):
        kenyaDate = kenyaDateTime(date, False)
        commentLine = '\t' + kenyaDate + ':\t' + str(count)
        resultInfo.append(commentLine)
    
    return '\n'.join(resultInfo)

def removeExtraCols(dataLine, keepActActee = False):
    '''
    Given dataLine--a single line from a processed prim8 data file that
    has been stripped and split--remove the values that have been deemed
    as superfluous for our observers' needs.
    
    Assumes that dataLine is of the following format:
    dataLine[0]        Sample Type
    dataLine[1]        Observer
    dataLine[2]        Date
    dataLine[3]        Time, or Sample Start time
    dataLine[4]        Group Abbreviation
    dataLine[5]        Actor, or Focal
    dataLine[6]        Sample Type, or Act
    dataLine[7]        Sample End time, or Actee, or "NULL" (for PNTs)
    dataLine[8]        Food code, neighbor code, or doesn't exist
    
    Returns a new list of strings, containing only the values from
    positions 2, 3, and 5.  When "keepActActee" is True, also keeps
    positions 6 and 7.
    '''
    outLine = []
    outLine.append(dataLine[2])
    outLine.append(dataLine[3])
    outLine.append(dataLine[5])
    
    if keepActActee:
        outLine.append(dataLine[6])
        outLine.append(dataLine[7])
    
    return outLine

def kenyaFixLine(dataLine, keepActActee = False):
    '''
    Given dataLine--a single line from a processed prim8 data file that
    has been stripped and split--fix its date and remove superfluous
    columns.
    
    Returns a new list of strings.
    '''
    outLine = kenyaFixDateInLine(dataLine)
    
    return removeExtraCols(outLine, keepActActee)
