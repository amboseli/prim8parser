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

def errorCheck (inFilePath, outFilePath, guiName):
    '''
    Checks the data in the file at inFilePath for possible errors.
    Also does some counting of basic statistics about the data, e.g. (how many focals, how many adlibs, etc.)
    Errors, alerts, and statistics will be written to the file at outFilePath.
    To be used in a GUI, guiName.  Quits the GUI at end of function. 
    Prints a message that the process is complete.
    Returns nothing.
    
    Consider breaking this up into some smaller functions?  Maybe run the counts and by-line analyses for each date instead of just once for everything?  Another day.
    '''
    ##Declare constants
    focalCode = 'HDR'
    pointCode = 'PNT'
    neighborCode = 'NGH'
    adlibCode = 'ADL'
    noteCode ='TXT'
    emptyValue = 'NULL'
    outOfSightValue = 'OOS'
    
    print "Creating export file"
    outFile = open(outFilePath,'w')
    
    outMsg = datetime.today().strftime('%Y-%m-%d %H:%M:%S') + ' analysis of file ' + inFilePath 
    print "Writing header message:", outMsg
    outFile.write(outMsg + '\n\n')
    
    print "Opening import file"
    impFile = open(inFilePath, 'r')
    impEvents = impFile.readlines()
       
    print "Adding all lines to allEvents list"
    allEvents =  [line.strip().split('\t') for line in impEvents] ##List of all lines read from the import file (impFile)
    allEvents.pop(0) ##Remove the "Parsed data..." line at the top
    
    firstEventTime = getDateTime(allEvents[0], 2, 3).strftime('%Y-%m-%d %H:%M:%S')
    lastEventTime = getDateTime(allEvents[-1], 2, 3).strftime('%Y-%m-%d %H:%M:%S')
    outMsg = 'Data begins at ' + firstEventTime + ' and ends at ' + lastEventTime
    outFile.write(outMsg + '\n\n')    
    
    outMsg = str(len(allEvents)) + ' total data lines recorded.'
    outFile.write(outMsg + '\n')
    
    focals = [line for line in allEvents if line[0] == focalCode] ##List of all the lines that begin new focals, i.e. the "HDR" lines. Will be useful for adding data to SAMPLES.
    points = [line for line in allEvents if line[0] == pointCode] ##List of all the PNT lines
    outMsg = str(len(points)) + ' points recorded during ' + str(len(focals)) + ' focal samples.'
    outFile.write(outMsg + '\n')
    
    adlibs = [line for line in allEvents if line[0] == adlibCode] ##List of all the lines that are adlibs, i.e. groomings and agonisms.
    outMsg = str(len(adlibs)) + ' ad-lib interactions recorded.'
    outFile.write(outMsg + '\n')
    
    notes = [line for line in allEvents if line[0] == noteCode] ##List of all the lines that are text notes.
    outMsg = str(len(notes)) + ' free-form text notes recorded.'
    outFile.write(outMsg + '\n')
    
    outFile.write('\nErrors and alerts:\n')
    
    ##Check for the same individual being sampled more than once on the same day
    focalInfo = [(focal[2],focal[5]) for focal in focals] ##Make list of (date (as string), sname) tuples of all focals
    duplicateFocals = set() ##Will store any duplicate (date, sname) focals.
    for focal in focalInfo:
        if focalInfo.count(focal) > 1:
            duplicateFocals.add(focal)
    if len(duplicateFocals) > 0 :
        outMsg = "Found duplicate focal samples:" 
        print outMsg
        outFile.write(outMsg + '\n')
        duplicateList = list(duplicateFocals)
        duplicateList.sort()
        for dupFocal in duplicateList:
            outMsg = '\t' + str(dupFocal)
            print outMsg
            outFile.write(outMsg + '\n')
    
    ##Check if >1 group was sampled in a single day.
    focalInfoSet = set([(focal[2],focal[4]) for focal in focals]) ##Set of (date (as string), group) tuples from all focals
    dateCountDict = {}
    for (focalDate, focalGrp) in focalInfoSet:
        if focalDate not in dateCountDict:
            dateCountDict[focalDate] = [focalGrp] 
        else:
            dateCountDict[focalDate].append(focalGrp)
    for (k,v) in dateCountDict.iteritems():
        if len(v) > 1:
            outMsg = "Found multiple groups sampled on same day: " + k + " , in " + ",".join(v)
            print outMsg
            outFile.write(outMsg + '\n')

    ##Check for multiple or unusual observers
    ##Because of the way we added observer when parsing the prim8 import file, the same "observer" value is used for all lines.
    ##So we need only look at one line, not iterate through everything.
    if len(allEvents[0][1]) != 3: ##then the "observer" isn't simply someone's three-letter initials.
        outMsg = 'Unusual observer recorded: ' + allEvents[0][1]
        print outMsg
        outFile.write(outMsg + '\n')
    
    outFile.write('\n')
    ##Initialize some variables that will be used to determine how to analyze many of the lines in allEvents
    isFocal = False ##Indicates if the current line being checked was during a focal sample. Will be toggled TRUE<-->FALSE a lot while iterating through allEvents.
    focalEndTime = datetime.strptime('1909-01-01 01:01:01', '%Y-%m-%d %H:%M:%S') ##Indicates when the current focal is supposed to end. The 1909 time is a placeholder.
    numNeighbors = 0 ##Tells how many neighbor lines have been recorded in the current point sample
    numPoints = 0 ##Tells how many points have been recorded in the current focal sample
    currentFocTime = '' ##Will indicate the focal start time from the last analyzed HDR row. This will just be used in error/alert messages.
    currentFocLine = 0 ##The line number (in the source file) of the HDR row of the current focal.
    currentPntTime = '' ##Will indicate the time from the last analyzed PNT row. Just for error/alert messages.
    currentPntLine = 0 ##The line number (in the source file) of the most-recent PNT row.
    currentPntActivity = '' ##The activity/position info recorded with each point.
    
    for (n, line) in enumerate(allEvents): ##Line number in the file is (n+2), because 1) we're counting from 0 and 2) we've already popped out the first line
        print "Checking line", str(n+2)
        if isFocal and getDateTime(line, 2, 3) > focalEndTime: ##Then the formerly-ongoing focal is over. Do some checking of its data.
            isFocal = False
            if numNeighbors != 3 and numPoints > 0 and currentPntActivity != outOfSightValue: ##Make sure 3 neighbors recorded for last point (if any PNTs), but only if that last PNT was in sight.
                alertMsg = 'Line ' + str(currentPntLine) + ': Focal ends before 3 neighbors recorded for ' + currentPntTime + ' point'
                print alertMsg
                outFile.write(alertMsg + '\n')
            numNeighbors = 0
            if numPoints > 10:
                alertMsg = 'Line ' + str(currentFocLine) + ': ' + str(numPoints) + ' points recorded for ' + currentFocTime + ' focal sample. Maximum 10 allowed.'
                print alertMsg
                outFile.write(alertMsg + '\n')
            numPoints = 0
            currentFocTime = ''
            currentFocLine = 0
            currentPntTime = ''
            currentPntLine = 0
            currentPntActivity = ''
        if line[0] == focalCode:
            isFocal = True
            numNeighbors = 0 ##Pretty sure this will already be true, but just in case
            numPoints = 0 ##Pretty sure this will already be true, but just in case
            currentFocTime = line[3]
            currentFocLine = n + 2
            focalEndTime = getDateTime(line, 2, -1)
            currentPntTime = ''
            currentPntLine = 0
            currentPntActivity = ''
        elif line[0] == pointCode:
            if not isFocal: ##Then this point was somehow recorded outside the duration of a focal (Pretty sure Prim8 forbids this)
                alertMsg = 'Line ' + str(n+2) + ": PNT sample outside of a focal sample"
                print alertMsg
                outFile.write(alertMsg + '\n')
            if numPoints > 0 : ##Then this isn't the first point recorded for this focal sample. Make sure the previous point had 3 neighbors.
                if numNeighbors != 3 and currentPntActivity != outOfSightValue: ##If the last point was out of sight, no neighbors expected.
                    alertMsg = 'Line ' + str(currentPntLine) + ': New PNT at line ' + str(n+2) + ' before 3 neighbors recorded for ' + currentPntTime + ' point'
                    print alertMsg
                    outFile.write(alertMsg + '\n')
            currentPntTime = line[3]
            currentPntLine = n + 2
            numPoints += 1
            numNeighbors = 0
            currentPntActivity = line[5]
        elif line [0] == neighborCode:
            if not isFocal: ##Then this neighbor was somehow recorded outside the duration of a focal (Pretty sure Prim8 forbids this)
                alertMsg = 'Line ' + str(n+2) + ": NGH line outside of a focal sample"
                print alertMsg
                outFile.write(alertMsg + '\n')
            if numPoints == 0: ##Then this neighbor was recorded without first making a PNT line
                alertMsg = 'Line ' + str(n+2) + ": NGH line before a PNT line"
                print alertMsg
                outFile.write(alertMsg + '\n')
            if numNeighbors == 3: ##Trying to add a 4th neighbor
                alertMsg = 'Line ' + str(n+2) + ": 4th neighbor detected for a single point"
                print alertMsg
                outFile.write(alertMsg + '\n')
            numNeighbors += 1
        elif line [0] == adlibCode:
            if line[4] == line [6]: ##actor and actee the same
                alertMsg = 'Line ' + str(n+2) + ": Actor == Actee in " + str(line)
                print alertMsg
                outFile.write(alertMsg + '\n')
            if line[6] == emptyValue: ##actee is NULL
                alertMsg = 'Line ' + str(n+2) + ": Actee is NULL in " + str(line)
                print alertMsg
                outFile.write(alertMsg + '\n')
            if line[5] in ['E','M','C']: ##Act is behavior we no longer allow in Prim8
                alertMsg = 'Line ' + str(n+2) + ": Act " + line[5] + "no longer allowed"
                print alertMsg
                outFile.write(alertMsg + '\n')
        elif line [0] == noteCode:  
            print "Note. Nothing to do on line", line
        else:
            print "Line", line, "is not recognized"
    
    print "Closing export file"
    outFile.close()
    outMsg = "Finished checking data in " + inFilePath
    print outMsg
    guiName.quit()

if __name__ == '__main__':
    ##Make a GUI to select import and export file names/locations
    master = Tk()
    Label(master, text="Import file:").grid(row=0)
    Label(master, text="Export file").grid(row=1)

    e1 = Entry(master) ##for import file path
    e2 = Entry(master) ##for output file path

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)

    Button(master, text='Choose', command = e1.insert(1000, askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='Select a processed file to analyze:'))).grid(row=0, column=2)
    Button(master, text='Choose', command = e2.insert(1000, asksaveasfilename(defaultextension='.txt', title='Name of the analyzed data file?'))).grid(row=1, column=2)
    Button(master, text='Accept', command = errorCheck(e1.get(), e2.get(), master)).grid(row=2)

    master.mainloop()
    
    ##impPath = askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='Select a processed prim8 file:')
    ##impPath = './../output_test.txt'

    ##outPath = asksaveasfilename(defaultextension='.txt', title='Name for the error summary file?')
    ##outPath = './../file_summary.txt'
    
    ##print errorCheck(impPath, outPath)

    
    