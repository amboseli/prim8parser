'''
Created on 27 Aug 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

    Functions used to clean and process data from the prim8 import file into data usable by the rest of the program.

'''
import csv
from datetime import datetime, timedelta

def removeExtraNewLines(filePath):
    '''
    Given a file's path:
        1) opens the file,
        2) reads through the data and removes all newline characters (but not carriage returns),
        3) adds a newline after each carriage return,
        4) splits the text into a list of strings separated by newlines, then
        5) closes the file.
    Returns a list of strings: one string per line from file, with carriage returns/newlines removed.
    
    Useful because the team's data occasionally includes newline characters (but not carriage returns) in the middle of their data, e.g. "Out of S\night"  
    It's not yet clear how this is happening, but these unwanted newlines cause trouble when reading the data file one line at a time.  
    '''
    openedFile = open(filePath,'r')
    print "Reading raw input file"
    fullText = openedFile.read()
    fullText = fullText.replace(u"\u000A","") ##Replace all newlines ('\n') with nothing
    fullText = fullText.replace(u"\u000D",u"\u000D\u000A") ##Replace all carriage returns ('\r') with carriage return, new line ('\r\n')
    print "Finished checking for unwanted newlines"
    openedFile.close()
    return fullText.splitlines()

def cleanRawData(filePath):
    '''
    Given a file path:
        1) opens the file,
        2) processes its data into a list of lists of strings, ready to be parsed, and
        3) closes the file.
    Performs comma-separated split using csvreader to account for the possibility of commas in data fields.
    Returns a list of lists of strings: each (inner) list of strings represents one line of data from openedFile. 
    '''
    fullText = removeExtraNewLines(filePath) # File is opened and closed here
    fullText = csv.reader(fullText, delimiter=',', quotechar='"')
    return fullText

def makeAllDicts(filePath):
    '''
    Given a file path, reads and processes the file's data into a dictionary of dictionaries.
    Each of the "inner" dictionaries is essentially one "table" of data from the input file.

    The names of each of the "inner" dictionaries is given by the local list, "p8TableList".
    Returns the dictionary of dictionaries.
    '''
    allLines = cleanRawData(filePath) # Opens and closes file
    
    fullDict = {} ##The big, bad dictionary of dictionaries returned by this function
    
    from constants import p8TableList
     
    for table in p8TableList: ##Create a bunch of empty dictionaries, with names from p8TableList
        fullDict[table] = {}
    
    currentDictName = '' ##Used in the below "for" loop, to indicate which dictionary to add all the data
    for n,line in enumerate(allLines): ##Enumerating and adding n to allow the return of line numbers in case there's an error
        ##TODO: Change the way line number is returned. If the input file has any spurious newline characters, then n does not accurately indicate line number in the original file.
        if len(line) == 1: ##Then the line should indicate the beginning of a new table.  Until a new table starts, all following lines should be added to the dictionary of this name.
            if line[0] not in p8TableList: ##Then there's a problem in the file
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
    fullDict = addInstancesModifiersDict(fullDict)
    print 'Finished creating dictionary of dictionaries!'
    return fullDict

def addInstancesModifiersDict(masterDict):
    '''
    Given the big main dictionary of dictionaries masterDict, which is assumed to contain a "modifiers" dictionary.
    Adds another dictionary to masterDict, whose name is specified in constants.py as dictInstMods.
    
    This dictionary shows an association between behavior instances and modifiers. The dictionary's keys are behavior_instancesid's
      from the modifiers table.  Values are the modifiers_id's. 
    
    Returns the updated masterDict.
    '''
    ##TODO: Don't bother making a new dictionary, and just make a function that fetches data from the modifiers table as it is?
    from constants import dictInstMods, p8modifiers
    modifierIDs = sorted(masterDict[p8modifiers].keys()) ##Get list of all the modifiers_id's
    modifierIDs.pop()  ##Remove the key for the modifiers table "legend"
    masterDict[dictInstMods] = {}
    for mod_id in modifierIDs:
        instance_id = masterDict[p8modifiers][mod_id][0]
        masterDict[dictInstMods][instance_id] = mod_id
    print "Dictionary", dictInstMods, "populated"
    return masterDict

def rawGetDateTime (itemList, yearIndex):
    '''
    Given a list (itemList, presumably the value returned from a dictionary created from the Prim8 import file), and the index (yearIndex) in that list where the "Year" value is stored.
    (Assumes that "Year" is followed by Month, Day, Time)
    Outputs the date and time as a single "datetime" object.
    '''
    print "Making date/time beginning at", itemList[yearIndex], "from list", itemList
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

def getAllObservations(masterDict):
    '''
    Given the big main dictionary of dictionaries masterDict.
    
    Makes a list of (datetime, tablename, table key) tuples for ALL observations that we want to record.
    Collects data from the tables listed in the observationTables list in constants.py
    
    Before returning, the list is sorted.
    
    Returns a list of tuples.
    '''
    from constants import observationTables
    
    eventList = []
    for tableName in observationTables:
        addEventKeys(eventList, masterDict[tableName], tableName)
    eventList.sort()
    return eventList

def getCodes(codeFilePath, longIndex, shortIndex):
    '''
    Given the path (codeFilePath) for a tab-delimited txt file, adds the short and long codes to two separate lists: one list for short codes, one for long codes.
        --The "long" code in codeFile is at the (longIndex)'th index in each line (assuming the line is split).
        --The "short" code in codeFile is at the (shortIndex)'th index in each line (assuming the line is split).
    Codes will be added to both lists simultaneously, so longList[n] will correspond to shortList[n].
    Returns two lists: first the one with long codes, then the one with short codes.
    
    Intended for cases like group names and food codes, where names/values used in Prim8 don't quite align with what we use in Babase.
    '''
    longCodes = []
    shortCodes = []
    codeFile = open(codeFilePath,'r')
    allCodes = codeFile.readlines()
    codeFile.close()
    for code in allCodes:
        cleanCode = code.strip().split("\t")
        longCodes.append(cleanCode[longIndex].upper())
        shortCodes.append(cleanCode[shortIndex].upper())
    return longCodes, shortCodes

def getObserver(masterDict, eventKey):
    '''
    Given masterDict, a dictionary of dictionaries whose contents include dictionaries called "observers" and "behaviorinstances",
    and eventKey, an integer representing a key in the "behaviorinstances" dictionary.
    Returns the initials of the observer (a string) who recorded the instance referred-to by eventKey.
    '''
    from constants import p8observers, p8behaviorinstances
    return masterDict[p8observers][(masterDict[p8behaviorinstances][eventKey][9])][2]

def multipleObservers(masterDict):
    '''
    Given the big main dictionary of dictionaries masterDict, which is assumed to contain a "observers" dictionary.
    Checks if more than one observer's initials are used.
    Returns True (yes, more than one observer) or False (0-1 observers).
    '''
    from constants import p8observers
    obs = [value[2] for (key, value) in masterDict[p8observers].iteritems() if type(key) == int]
    return len(obs) > 1

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
    from constants import p8behaviors, p8behaviorinstances, p8behaviortypes, p8individuals, p8modifiers, dictInstMods,neighborAbbrev, emptyAbbrev, proxBehavName
    
    outList = [] ##List of strings that will be joined together
    
    eventTypeID =  masterDict[p8behaviors][(masterDict[p8behaviorinstances][eventKey][1])][7] ##Look up behavior type id
    eventType = masterDict[p8behaviortypes][eventTypeID][1] ##Using behavior type id, get the actual abbrev for that behavior type
    if eventType == proxBehavName: ##Then it's a "neighbor" line. Let's use a shorter abbreviation.
        eventType = neighborAbbrev
    outList.append(eventType.upper()) ##Add code to indicate what kind of line this is
    if instanceObserver == 'NOT GIVEN':
        observer = getObserver(masterDict, eventKey)
    else:
        observer = instanceObserver
    outList.append(observer.upper())
    outList.append(dayTime.date().isoformat())  ##Add date  
    outList.append(dayTime.time().isoformat()) ##then time
    actorID = masterDict[p8individuals][(masterDict[p8behaviorinstances][eventKey][0])][1] ##Get actor
    outList.append(actorID.upper())
    actID = masterDict[p8behaviors][(masterDict[p8behaviorinstances][eventKey][1])][1]  ##Get act
    outList.append(actID.upper())
    if masterDict[p8behaviorinstances][eventKey][2] == '': ##There's no actee. We don't want to pass '' to the "individuals" dictionary
        acteeID = emptyAbbrev
    else:
        acteeID = str(masterDict[p8individuals][(masterDict[p8behaviorinstances][eventKey][2])][1]) ##Convert to string in case the actee is 997, 998
    outList.append(acteeID.upper())
    if eventKey in masterDict[dictInstMods]: ##then there was a modifier recorded with this event as well
        modKey = masterDict[dictInstMods][eventKey] ##Get the modifiers ID
        modifier = masterDict[p8modifiers][modKey][1] ##Get the modifier (a string)
        foodsLong, foodsShort = getCodes('./foodcodes.txt', 1, 0) # Get food codes
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
    from constants import p8individuals, p8focalfollows, focalAbbrev, p8groups
    
    ##Get a corrected list of group names, because prim8 doesn't comprehend group names with apostrophes. E.g. we want "ACA", not "acacia".  Prim8 can't handle "acacia's".
    groupsLong, groupsShort = getCodes('./groupcodes.txt', 3, 2)
    
    outList = [] ##List of strings that will be joined together
    
    outList.append(focalAbbrev.upper()) ##Add a code to indicate that this line begins a new focal sample
    outList.append(focalObserver.upper())
    outList.append(dayTime.date().isoformat())  ##Add date  
    outList.append(dayTime.time().isoformat()) ##then time
    focalGrpID = masterDict[p8individuals][(masterDict[p8focalfollows][eventKey][0])][4] ##Get group ID number, based on the residence of the focal individual
    focalGrpName = (masterDict[p8groups][focalGrpID][0])  ##Get group name
    if focalGrpName.upper() in groupsLong: ##This _should_ be always true
        grpIndex = groupsLong.index(focalGrpName.upper())
        print ("Replacing group name '" + focalGrpName + "' with '" + groupsShort[grpIndex] + "'")
        focalGrpName = groupsShort[grpIndex]
    outList.append(focalGrpName.upper())
    focalID = masterDict[p8individuals][(masterDict[p8focalfollows][eventKey][0])][1]
    outList.append(focalID.upper())
    focDuration = masterDict[p8focalfollows][eventKey][5]
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
    from constants import noteAbbrev, p8adlib
    outList = [] ##List of strings that will be joined together
    outList.append(noteAbbrev.upper()) ## Add code to indicate that this line is a free-form text note
    outList.append(adlibObserver.upper()) ## Observer
    outList.append(dayTime.date().isoformat()) ## Date
    outList.append(dayTime.time().isoformat()) ## Time
    outList.append(masterDict[p8adlib][eventKey][-1]) ##Note
    outLine = '\t'.join(outList)
    print outLine
    return str(outLine + '\n')

def writeAll(outputFilePath, appVersion, masterDict):
    '''
    Does the following:
        1) reads the sorted (date/time, event dictionary name, event key) tuples in eventList
        2) converts them to readable text
        3) opens a file for writing, specificed by outputFilePath
        4) writes the text (from #2) to the file
    outputFilePath is a string.
    appVersion is a string that should indicate which version of the Prim8 app generated the data. 
    masterDict is the big dictionary of dictionaries that stores all the data.
    
    Checks if multiple observers are recorded in the data.  If only one, that same observer will be used throughout the data without looking it up in every line.
    If more than one observer:
        For behavior instances, looks up the noted observer in each line.
        For focal follows and "adlibs" (text notes), will use the same observer used in the last behavior instance.
        For focal follows and "adlibs" noted before any behavior instances, will use the observer noted in the first behavior AFTER the follow/adlib.
    
    Returns a message, ideally to print to the console, that the process is complete.
    '''
    from constants import p8adlib, p8observers, p8behaviorinstances, p8focalfollows
    
    ##Create an eventList with all the different behaviors and notes that we want recorded.
    ##Having them all in one list helps us sort different kinds of data chronologically.
    eventList = getAllObservations(masterDict)
    
    ##Open file for writing at outputFilePath
    outputFile = open(outputFilePath, 'w') 
    
    outLine = 'Parsed data from AmboPrim8, version ' + str(appVersion)+'\n' ##Start every file with this line 
    outputFile.write(outLine)
    if multipleObservers(masterDict): ##then we'll need to manually check the observer for each line.
        lastObserver = '' ##Will be updated in the loop
        for (eventDayTime, eventTable, tableKey) in eventList:
            if eventTable == p8behaviorinstances:
                outLine, lastObserver = writeInstance(eventDayTime, tableKey, masterDict)
                outputFile.write(outLine)
            elif eventTable == p8focalfollows:
                if lastObserver == '': ##we haven't had a behavior yet with an observer. So look forward to the next behavior instance and get its observer.
                    print "Focal started with no previous observer. Getting observer."
                    soonestBehaviorKey = [key for (time, table, key) in eventList if table == p8behaviorinstances and time > eventDayTime].pop(0)
                    lastObserver = getObserver(masterDict, soonestBehaviorKey)
                    print "Presumed observer is", lastObserver
                    outLine = writeFocalFollow(eventDayTime, tableKey, masterDict, lastObserver)
                else:
                    outLine = writeFocalFollow(eventDayTime, tableKey, masterDict, lastObserver)
                outputFile.write(outLine)
            elif eventTable == p8adlib:
                if lastObserver == '': ##we haven't had a behavior yet with an observer. So look forward to the next behavior instance and get its observer.
                    print "Adlib note recorded with no previous observer. Getting observer."
                    soonestBehaviorKey = [key for (time, table, key) in eventList if table == p8behaviorinstances and time > eventDayTime].pop(0)
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
        onlyObserver = [value[2] for (key, value) in masterDict[p8observers].iteritems() if type(key) == int].pop()
        print onlyObserver
        for (eventDayTime, eventTable, tableKey) in eventList:
            if eventTable == p8behaviorinstances:
                outLine, lastObserver = writeInstance(eventDayTime, tableKey, masterDict, onlyObserver)
                outputFile.write(outLine)
            elif eventTable == p8focalfollows:
                outLine = writeFocalFollow(eventDayTime, tableKey, masterDict, onlyObserver)
                outputFile.write(outLine)
            elif eventTable == p8adlib:
                outLine = writeAdLib(eventDayTime, tableKey, masterDict, onlyObserver)
                outputFile.write(outLine)
            else:
                print "Unrecognized table from:", (eventDayTime, eventTable, tableKey)
                outputFile.write('Unable to parse data'+'\n')
    print "Closing export file at", outputFilePath
    outputFile.close()
    return 'Finished writing all data!'