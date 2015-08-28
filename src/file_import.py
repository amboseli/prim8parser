'''
Created on 29 Jul 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
''' 
from datetime import datetime, timedelta
from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from cleanInputFile import cleanInputData

def makeAllDicts(openedFile):
    '''
    Given an opened file, reads processes the data into a dictionary of dictionaries.  Each of the "inner" dictionaries is essentially one "table" of data from the input file.
    Closes the opened file.
    The names of each of the "inner" dictionaries is given by the local list, "tableList".
    Returns the dictionary of dictionaries.
    '''
    allLines = cleanInputData(openedFile) ##Closes file
    
    fullDict = {} ##The big, bad dictionary of dictionaries returned by this function
    
    ##These NEED to be spelled the same way as they are in the data file.  Case sensitive.  Order in this list is not important, however.
    tableList = ['adlib', 'sites', 'observers', 'groups','species','individuals', 'biologicalsamples','coordinatesystem','locations','workcalendars','behaviortypes','behaviors','focalfollows','scans','behaviorinstances','focalbehaviors','scanbehaviors','modifiers'] 
    
    for table in tableList: ##Create a bunch of empty dictionaries, with names from tableList
        fullDict[table] = {}
    
    currentDictName = tableList[0] ##Used in the below "for" loop, to indicate which dictionary to add all the data
    for n,line in enumerate(allLines): ##Enumerating and adding n to allow the return of line numbers in case there's an error
        ##TODO: Change the way line number is returned. If the input file has any spurious newline characters, then n does not accurately indicate line number in the original file.
        if len(line) == 1: ##Then the line should indicate the beginning of a new table.  Until a new table starts, all following lines should be added to the dictionary of this name.
            if line[0] not in tableList: ##Then there's a problem in the file
                print "Problem at line", (n+1), ":", line[0], " is not a recognized table name"
                fullDict = {} ##Empty the dictionary, to essentially halt any processes that may come after
                return fullDict
            print 'Begin', line[0], 'dictionary.'
            currentDictName = line[0]
        else: ##Line should be actual data to add to a table
            for x,item in enumerate(line): ##Check for numbers that are saved as strings
                if item.isdigit(): ##then item is a number and shouldn't stay a string
                    line[x] = int(item)
            fullDict[currentDictName][line[0]] = line[1:] ##Set the first column of the data as the key, everything else as the value
            ##print 'Added', line[1:], "to", currentDictName, 'with key #', line[0]
    print 'Finished creating dictionary of dictionaries!'
    return fullDict

def rawGetDateTime (itemList, yearIndex):
    '''
    Feed a list (itemList, presumably the value returned from a dictionary created from the Prim8 import file), and the index (yearIndex) where the "Year" value is stored.
    (Assumes that "Year" is followed by Month, Day, Time)
    Outputs the date and time as a single "datetime" object.
    '''
    ##print "Making date/time beginning at", itemList[yearIndex], "from list", itemList
    thisYear = itemList[yearIndex]
    thisMonth = itemList[yearIndex+1]
    thisDay = itemList[yearIndex+2]
    timeList = itemList[yearIndex+3].split(":")
    thisHour = int(timeList[0])
    thisMinute = int(timeList[1])
    thisSecond = int(timeList[2])
    outDateTime = datetime(thisYear, thisMonth, thisDay, thisHour, thisMinute, thisSecond)
    ##print "Date/time is", outDateTime
    return outDateTime

def getYearIndex (someDictionary):
    '''
    Given a dictionary where: (these are assumptions, not checked-for in the code)
        1) all the values are lists of strings
        2) all but one of the keys are integers
        3) the one non-integer key is a "legend" that defines the other values
        4) (preferably) one of the items in the "legend" values == "Year"
    Return the index in the list of strings where the "Year" value occurs.  Or -1.
    '''
    dictKeys = sorted(someDictionary.keys()) ##Get all the keys, and sort them
    keyTableLegend = dictKeys[-1] ##When sorted, the one non-integer key will be after all the integers
    tableLegend = someDictionary[keyTableLegend]
    index = 0
    for i in tableLegend:
        if i.lower() == 'year':
            return index
        else:
            index += 1
    return -1

def addEventKeys (targetList, sourceDictionary, dictName):
    '''
    Given a dictionary (sourceDictionary) to read from, adds (datetime, dictName, dictionary key) tuples to the targetList.
    Used to combine data ("events") of different types together into a single list that can easily be sorted by time.  
    Returns the appended list. (or, if there were no data in targetList to add, returns the unappended list)  
    '''
    ##Get and sort all the keys in the dictionary. Except for the "legend", these should just be ID numbers.
    eventKeys = sorted(sourceDictionary.keys())
    if len(eventKeys) == 0: ##Then there were no events recorded in the given table. 
        return targetList
    eventKeys.pop() ##Remove the table "legend". As the only non-integer key, it will be last in the sorted list.
    for i in eventKeys:
        yrIdx = getYearIndex(sourceDictionary)
        eventDateTime = rawGetDateTime(sourceDictionary[i], yrIdx)
        finalInfo = (eventDateTime, dictName, i) 
        targetList.append(finalInfo)
    return targetList

def prim8VersionInput():
    global prim8Version, master, impPath, outPath
    impPath = e1.get()
    outPath = e2.get()
    prim8Version = e3.get()
    master.quit()
    print "Closed tk window"
    
def getCodes(codeFile, longIndex, shortIndex):
    '''
    Given a tab-delimited txt file codeFile, adds the short and long codes to two separate lists: one list for short codes, one for long codes.
    The "long" code in codeFile is at the (longIndex)'th index in each line (assuming the line is split).
    The "short" code in codeFile is at the (shortIndex)'th index in each line (assuming the line is split).
    Codes will be added to both lists simultaneously, so longList[n] will correspond to shortList[n].
    Returns two lists: first the one with long codes, then the one with short codes.
    
    Intended for cases like group names and food codes, where names/values used in Prim8 don't quite align with what we use in Babase.
    '''
    longCodes = []
    shortCodes = []
    allCodes = codeFile.readlines()
    for code in allCodes:
        cleanCode = code.strip().split("\t")
        longCodes.append(cleanCode[longIndex].upper())
        shortCodes.append(cleanCode[shortIndex].upper())
    print "Finished getting codes"
    return longCodes, shortCodes

def getObserver(masterDict, eventKey):
    '''
    Given masterDict, a dictionary of dictionaries whose contents include dictionaries called "observers" and "behaviorinstances",
    and eventKey, an integer representing a key in the "behaviorinstances" dictionary.
    Returns the initials of the observer (a string) who recorded the instance referred-to by eventKey.
    '''
    return masterDict['observers'][(allData['behaviorinstances'][eventKey][9])][2]

def multipleObservers(masterDict):
    '''
    Given the big main dictionary of dictionaries masterDict, which is assumed to contain a "observers" dictionary.
    Checks if more than one observer's initials are used.
    Returns True (yes, more than one observer) or False (0-1 observers).
    '''
    obs = [value[2] for (key, value) in masterDict['observers'].iteritems() if type(key) == int]
    return len(obs) > 2

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
    global neighborAbbrev, instances_modifiers, foodsLong, foodsShort
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
    ##Declare constants
    focalAbbrev = 'HDR' ##Abbreviation for output file to indicate that the line begins a new focal sample
    neighborAbbrev = 'NGH' ##Abbreviation for output file to indicate that the line is a focal neighbor
    noteAbbrev = 'TXT' ##Abbreviation for output file to indicate that the line is freeform text

    ##Declare important global variables
    impPath = '' ##File path for the import file
    outPath = '' ##File path for the output file
    prim8Version = '1.150510'
    allData = {} ##Dictionary of dictionaries to be created from the import file
    noteList = [] ##List for (datetime, dictionary name, dictionary key) tuples for every line that we want recorded in the final output sheet
    instances_modifiers = {} ##Dictionary to note all the behavior instances where modifiers were also recorded (presumably only neighbor lines and points with food codes)
    foodsLong = [] ##List for food codes. This will hold the long name, e.g. "Grass corms of other or unknown species". 
    foodsShort = [] ##List for food codes.  This will hold the short name, e.g. "GRC".
    groupsLong = [] ##List for group names. This will hold the spelled-out name, as it was provided to the Prim8 app, e.g. "acacia" for Acacia's group
    groupsShort = [] ##List for group names. This will hold the abbreviation for the group's name, e.g. "ACA" for Acacia's group

    ##These NEED to be listed in the order they appear in the import file, and NEED to be spelled the same way as they are in the data file.
    tableList = ['adlib', 'sites', 'observers', 'groups','species','individuals', 'biologicalsamples','coordinatesystems','locations','workcalendars','behaviortypes','behaviors','focalfollows','scans','behaviorinstances','focalbehaviors','scanbehaviors','modifiers'] 

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

    print "Opening import file"
    ##impPath = askopenfilename(filetypes=(('Comma-separated','*.csv'),('All files','*.*')), title='Select a file to import:')
    impFile = open(impPath, 'r')
    ##impFile = open('./../import_test.csv', 'r')

    print "Creating allData dictionary"
    allData = makeAllDicts(impFile)


    ##Populate the noteList with all the different behaviors and notes that we want recorded.
    ##Having them all in one list helps us sort different kinds of data chronologically.

    noteList = addEventKeys(noteList, allData['behaviorinstances'], 'behaviorinstances') ##Add all the observed behaviors
    noteList = addEventKeys(noteList, allData['adlib'], 'adlib') ##Add any "adlib" notes (not the ABRP kind of "adlibs". Those are included in "instances")
    noteList = addEventKeys(noteList, allData['focalfollows'], 'focalfollows') ##Add the focal follow information. These will be similar to the "header" rows from the old Psion format.

    noteList.sort() ##Make the list chronological

    ##Populate the instances_modifiers dictionary 
    ##Keys are the behavior_instancesid's from the modifiers table, values are the modifiers_id
    modifierIDs = sorted(allData['modifiers'].keys()) ##Get list of all the modifiers_id's
    modifierIDs.pop()  ##Remove the key for the modifiers table "legend"
    for i in modifierIDs:
        instance_id = allData['modifiers'][i][0]
        instances_modifiers[instance_id] = i
    print "Dictionary instances_modifiers populated"

    ##Get the food codes, so we can note the short name, not the long one.
    foodsLong, foodsShort = getCodes(open('./foodcodes.txt','r'), 1, 0)

    ##Get a corrected list of group names, because prim8 doesn't comprehend group names with apostrophes. E.g. we want "ACA", not "acacia".  Prim8 can't handle "acacia's".
    groupsLong, groupsShort = getCodes(open('./groupcodes.txt', 'r'), 3, 2)

    print "Creating export file"
    ##outPath = asksaveasfilename(defaultextension='.txt', title='Name of the exported data file?')
    outFile = open(outPath, 'w')
    ##outFile = open('./../output_test.txt','w')
    
    ##Let's finally output something!
    print writeAll(outFile, noteList, prim8Version, allData)

    print "Closing export file at", outPath
    outFile.close()