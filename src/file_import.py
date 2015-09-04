'''
Created on 29 Jul 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
''' 
from datetime import datetime, timedelta
from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from cleanRawFile import *
from constants import *

def prim8VersionInput():
    global prim8Version, master, impPath, outPath
    impPath = e1.get()
    outPath = e2.get()
    prim8Version = e3.get()
    master.quit()
    print "Closed tk window"
    


def writeInstance(dayTime, eventKey, masterDict, instanceObserver='NOT GIVEN'):
    '''
    Parses data for a line from the behavior_instances table and adds it together to a list.
    The list is joined into a string, presumably to write to the outFile.
    dayTime is a datetime object and represents the date and time of the instance.
    eventKey is an integer and is the key for the "instances" dictionary corresponding to the instance.
    "masterDict" is the main dictionary of dictionaries used so often in this program. Presumed to be "allData".
    instanceObserver is the optional string of the observer's initials to use in the data.  If not given, observer will be looked-up in masterDict.
    Returns a tuple, the string that can be written to the outFile, and the "observer" string.
    '''
    global instances_modifiers, foodsLong, foodsShort
    outList = [] ##List of strings that will be joined together
    eventTypeID =  masterDict['behaviors'][(masterDict['behaviorinstances'][eventKey][1])][7] ##Look up behavior type id
    eventType = masterDict['behaviortypes'][eventTypeID][1] ##Using behavior type id, get the actual abbrev for that behavior type
    if eventType == 'proximity': ##Then it's a "neighbor" line. Let's use a shorter abbreviation.
        eventType = neighborAbbrev
    outList.append(eventType.upper()) ##Add code to indicate what kind of line this is
    if instanceObserver == 'NOT GIVEN':
        observer = getObserver(masterDict, eventKey)
    else:
        observer = instanceObserver
    outList.append(observer.upper())
    outList.append(dayTime.date().isoformat())  ##Add date  
    outList.append(dayTime.time().isoformat()) ##then time
    actorID = masterDict['individuals'][(masterDict['behaviorinstances'][eventKey][0])][1] ##Get actor
    outList.append(actorID.upper())
    actID = masterDict['behaviors'][(masterDict['behaviorinstances'][eventKey][1])][1]  ##Get act
    outList.append(actID.upper())
    if masterDict['behaviorinstances'][eventKey][2] == '': ##There's no actee. We don't want to pass '' to the "individuals" dictionary
        acteeID = 'NULL'
    else:
        acteeID = str(masterDict['individuals'][(masterDict['behaviorinstances'][eventKey][2])][1]) ##Convert to string in case the actee is 997, 998
    outList.append(acteeID.upper())
    if eventKey in instances_modifiers: ##then there was a modifier recorded with this event as well
        modKey = instances_modifiers[eventKey] ##Get the modifiers ID
        modifier = masterDict['modifiers'][modKey][1] ##Get the modifier (a string)
        if modifier.upper() in foodsLong: ##Then the modifier is a food, and we want to change it to its abbreviation.
            foodIndex = foodsLong.index(modifier.upper())
            print ("Replacing food code '" + modifier + "' with '" + foodsShort[foodIndex] + "'")
            modifier = foodsShort[foodIndex] ##Replace the long food name with its short name
        outList.append(modifier.upper())
    outLine = '\t'.join(outList)
    print outLine
    return str(outLine + '\n'), observer

def writeFocalFollow(dayTime, eventKey, masterDict, focalObserver):
    '''
    Parses data for a line from the focalfollows table and adds it together to a list.
    The list is joined into a string, presumably to write to the outFile.
    dayTime is a datetime object and represents the date and time of the focal follow.
    eventKey is an integer and is the key for the "focalfollows" dictionary corresponding to the focal.
    masterDict is the big dictionary of dictionaries that stores all the data.
    focalObserver is a string, representing the initials of the observer of the focal sample.
    Returns the string that can be written to the outFile.
    '''
    global focalAbbrev, groupsLong, groupsShort
    outList = [] ##List of strings that will be joined together
    outList.append(focalAbbrev.upper()) ##Add code to indicate that this line begins a new focal sample
    outList.append(focalObserver.upper())
    outList.append(dayTime.date().isoformat())  ##Add date  
    outList.append(dayTime.time().isoformat()) ##then time
    focalGrpID = masterDict['individuals'][(masterDict['focalfollows'][eventKey][0])][4] ##Get group ID number, based on the residence of the focal individual
    focalGrpName = (masterDict['groups'][focalGrpID][0])  ##Get group name
    if focalGrpName.upper() in groupsLong: ##This _should_ be always true
        grpIndex = groupsLong.index(focalGrpName.upper())
        print ("Replacing group name '" + focalGrpName + "' with '" + groupsShort[grpIndex] + "'")
        focalGrpName = groupsShort[grpIndex]
    outList.append(focalGrpName.upper())
    focalID = masterDict['individuals'][(masterDict['focalfollows'][eventKey][0])][1]
    outList.append(focalID.upper())
    focDuration = masterDict['focalfollows'][eventKey][5]
    focDurDelta = timedelta(0,focDuration)
    endTime = dayTime + focDurDelta
    outList.append(endTime.time().isoformat())
    outLine = '\t'.join(outList)
    print outLine
    return str(outLine + '\n')

def writeAdLib(dayTime, eventKey, masterDict, adlibObserver):
    '''
    Parses data for a line from the adlibs table and adds it together to a list.
    The list is joined into a string, presumably to write to the outFile.
    dayTime is a datetime object and represents the date and time of the note.
    eventKey is an integer and is the key for the "adlibs" dictionary corresponding to the note.
    masterDict is the big dictionary of dictionaries that stores all the data.
    adlibObserver is a string, representing the initials of the observer of the note.
    Returns the string that can be written to the outFile.
    '''
    global noteAbbrev
    outList = [] ##List of strings that will be joined together
    outList.append(noteAbbrev.upper()) ##Add code to indicate that this line is a free-form text note
    outList.append(adlibObserver.upper())
    outList.append(dayTime.date().isoformat())
    outList.append(dayTime.time().isoformat())
    outList.append(masterDict['adlib'][eventKey][-1])
    outLine = '\t'.join(outList)
    print outLine
    return str(outLine + '\n')

def writeAll(outputFile, eventList, appVersion, masterDict):
    '''
    Reads the sorted (date/time, event dictionary name, event key) tuples in eventList, converts them to readable text, then writes the text to outputFile.
    Assumes outputFile is already open for writing.
    appVersion is a string that should indicate which version of the Prim8 app generated the data. 
    masterDict is the big dictionary of dictionaries that stores all the data.
    
    Checks if multiple observers are recorded in the data.  If only one, that same observer will be used throughout the data without looking it up in every line.
    If more than one observer:
        For behavior instances, looks up the noted observer in each line.
        For focal follows and "adlibs" (text notes), will use the same observer used in the last behavior instance.
        For focal follows and "adlibs" noted before any behavior instances, will use the observer noted in the first behavior AFTER the follow/adlib.
    
    Returns a message, ideally to print to the console, that the process is complete.
    '''
    eventList.sort() ##Should be sorted already, but just in case
    outLine = 'Parsed data from AmboPrim8, version ' + str(appVersion)+'\n' ##Start every file with this line 
    outputFile.write(outLine)
    if multipleObservers(masterDict): ##then we'll need to manually check the observer for each line.
        lastObserver = '' ##Will be updated in the loop
        for (eventDayTime, eventTable, tableKey) in eventList:
            if eventTable == 'behaviorinstances':
                outLine, lastObserver = writeInstance(eventDayTime, tableKey, masterDict)
                outputFile.write(outLine)
            elif eventTable == 'focalfollows':
                if lastObserver == '': ##we haven't had a behavior yet with an observer. So look forward to the next behavior instance and get its observer.
                    print "Focal started with no previous observer. Getting observer."
                    soonestBehaviorKey = [key for (time, table, key) in eventList if table == 'behaviorinstances' and time > eventDayTime].pop(0)
                    lastObserver = getObserver(masterDict, soonestBehaviorKey)
                    print "Presumed observer is", lastObserver
                    outLine = writeFocalFollow(eventDayTime, tableKey, masterDict, lastObserver)
                else:
                    outLine = writeFocalFollow(eventDayTime, tableKey, masterDict, lastObserver)
                outputFile.write(outLine)
            elif eventTable == 'adlib':
                if lastObserver == '': ##we haven't had a behavior yet with an observer. So look forward to the next behavior instance and get its observer.
                    print "Adlib note recorded with no previous observer. Getting observer."
                    soonestBehaviorKey = [key for (time, table, key) in eventList if table == 'behaviorinstances' and time > eventDayTime].pop(0)
                    lastObserver = getObserver(masterDict, soonestBehaviorKey)
                    print "Presumed observer is", lastObserver
                    outLine = writeAdLib(eventDayTime, tableKey, masterDict, lastObserver)
                else:
                    outLine = writeAdLib(eventDayTime, tableKey, masterDict, lastObserver)
                outputFile.write(outLine)
            else:
                print "Unrecognized table from:", (eventDayTime, eventTable, tableKey)
                outputFile.write('Unable to parse data'+'\n')
    else: ##there is only one observer, so this can move much faster by not re-looking up observer in every instance.
        print "Only one observer found. Get the only observer and don't look it up in each line."
        onlyObserver = [value[2] for (key, value) in masterDict['observers'].iteritems() if type(key) == int].pop()
        print onlyObserver
        for (eventDayTime, eventTable, tableKey) in eventList:
            if eventTable == 'behaviorinstances':
                outLine, lastObserver = writeInstance(eventDayTime, tableKey, masterDict, onlyObserver)
                outputFile.write(outLine)
            elif eventTable == 'focalfollows':
                outLine = writeFocalFollow(eventDayTime, tableKey, masterDict, onlyObserver)
                outputFile.write(outLine)
            elif eventTable == 'adlib':
                outLine = writeAdLib(eventDayTime, tableKey, masterDict, onlyObserver)
                outputFile.write(outLine)
            else:
                print "Unrecognized table from:", (eventDayTime, eventTable, tableKey)
                outputFile.write('Unable to parse data'+'\n')
    return 'Finished writing all data!'

if __name__ == '__main__':

    ##Declare important global variables
    impPath = '' ##File path for the import file
    outPath = '' ##File path for the output file

    allData = {} ##Dictionary of dictionaries to be created from the import file
    noteList = [] ##List for (datetime, dictionary name, dictionary key) tuples for every line that we want recorded in the final output sheet
    instances_modifiers = {} ##Dictionary to note all the behavior instances where modifiers were also recorded (presumably only neighbor lines and points with food codes)
    foodsLong = [] ##List for food codes. This will hold the long name, e.g. "Grass corms of other or unknown species". 
    foodsShort = [] ##List for food codes.  This will hold the short name, e.g. "GRC".
    groupsLong = [] ##List for group names. This will hold the spelled-out name, as it was provided to the Prim8 app, e.g. "acacia" for Acacia's group
    groupsShort = [] ##List for group names. This will hold the abbreviation for the group's name, e.g. "ACA" for Acacia's group

    ##Make a GUI to select import and export file names/locations
    master = Tk()
    Label(master, text="Import file:").grid(row=0)
    Label(master, text="Export file").grid(row=1)
    Label(master, text="Prim8 version #? (Probably 1.150510)").grid(row=2)

    e1 = Entry(master) ##for import file path
    e2 = Entry(master) ##for output file path
    e3 = Entry(master) ##Need to change Prim8 to include this value in the export

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)

    e3.insert(20, prim8Version)

    Button(master, text='Choose', command = e1.insert(100, askopenfilename(filetypes=(('Comma-separated','*.csv'),('All files','*.*')), title='Select a file to import:'))).grid(row=0, column=2, sticky='W', pady=4)
    Button(master, text='Choose', command = e2.insert(100, asksaveasfilename(defaultextension='.txt', title='Name of the exported data file?'))).grid(row=1, column=2, sticky='W', pady=4)
    Button(master, text='Accept', command = prim8VersionInput).grid(row=3, sticky='W',pady=4)

    master.mainloop()

    ##print "Opening import file"
    ##impPath = askopenfilename(filetypes=(('Comma-separated','*.csv'),('All files','*.*')), title='Select a file to import:')
    ##impFile = open(impPath, 'r')
    ##impFile = open('./../import_test.csv', 'r')

    print "Creating allData dictionary"
    allData = makeAllDicts(impPath)

    ##Populate the noteList with all the different behaviors and notes that we want recorded.
    ##Having them all in one list helps us sort different kinds of data chronologically.

    noteList = getAllObservations(allData)


    ##Get the food codes, so we can note the short name, not the long one.
    foodsLong, foodsShort = getCodes('./foodcodes.txt', 1, 0)

    ##Get a corrected list of group names, because prim8 doesn't comprehend group names with apostrophes. E.g. we want "ACA", not "acacia".  Prim8 can't handle "acacia's".
    groupsLong, groupsShort = getCodes('./groupcodes.txt', 3, 2)

    print "Creating export file"
    ##outPath = asksaveasfilename(defaultextension='.txt', title='Name of the exported data file?')
    outFile = open(outPath, 'w')
    ##outFile = open('./../output_test.txt','w')
    
    ##Let's finally output something!
    print writeAll(outFile, noteList, prim8Version, allData)

    print "Closing export file at", outPath
    outFile.close()