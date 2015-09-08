'''
Created on 27 Aug 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

    Functions used to clean and process data from the prim8 import file into data usable by the rest of the program.

'''

import csv
from datetime import datetime, timedelta
from constants import dictInstMods

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
    file.open(filePath,'r')
    print "Reading raw input file"
    fullText = filePath.read()
    fullText = fullText.replace(u"\u000A","") ##Replace all newlines ('\n') with nothing
    fullText = fullText.replace(u"\u000D",u"\u000D\u000A") ##Replace all carriage returns ('\r') with carriage return, new line ('\r\n')
    print "Finished checking for unwanted newlines"
    file.close()
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
    for id in modifierIDs:
        instance_id = masterDict[p8modifiers][id][0]
        masterDict[dictInstMods][instance_id] = id
    print "Dictionary", dictInstMods, "populated"
    return masterDict

def rawGetDateTime (itemList, yearIndex):
    '''
    Given a list (itemList, presumably the value returned from a dictionary created from the Prim8 import file), and the index (yearIndex) in that list where the "Year" value is stored.
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
        addEventKeys(eventList, masterDict, tableName)
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
    print "Finished getting codes from "
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