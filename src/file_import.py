'''
Created on 29 Jul 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
''' 
from datetime import datetime, timedelta
from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename

def removeExtraNewLines(file):
    '''
    Given an opened file, reads through the data and removes all newline characters (but not carriage returns), then adds a newline after each carriage return.
    Next, splits the text into a list of strings, separated by newlines.
    Closes the opened file.
    Returns a list of strings: one string per line from file, with carriage returns/newlines removed.
    
    Useful because the team's data occasionally includes newline characters (but not carriage returns) in the middle of their data, e.g. "Out of S\night"  
    It's not yet clear how this is happening, but these unwanted newlines cause trouble when reading the data file one line at a time.  
    '''
    print "Reading raw input file"
    fullText = file.read()
    fullText = fullText.replace(u"\u000A","") ##Replace all newlines ('\n') with nothing
    fullText = fullText.replace(u"\u000D",u"\u000D\u000A") ##Replace all carriage returns ('\r') with carriage return, new line ('\r\n')
    print "Finished checking for unwanted newlines"
    file.close()
    return fullText.splitlines()

def makeAllDicts(openedFile):
    '''
    Given an opened file, reads processes the data into a dictionary of dictionaries.  Each of the "inner" dictionaries is essentially one "table" of data from the input file.
    Closes the opened file.
    The names of each of the "inner" dictionaries is given by the local list, "tableList".
    Returns the dictionary of dictionaries.
    '''
    allLines = removeExtraNewLines(openedFile) ##Get data. Closes file.
    allLines = [line.split(",") for line in allLines] ##Split lines. The source file is CSV
    
    fullDict = {} ##The big, bad dictionary of dictionaries returned by this function
    
    ##These NEED to be spelled the same way as they are in the data file.  Case sensitive.  Order in this list is not important, however.
    tableList = ['adlib', 'sites', 'observers', 'groups','species','individuals', 'biologicalsamples','coordinatesystem','locations','workcalendars','behaviortypes','behaviors','focalfollows','scans','behaviorinstances','focalbehaviors','scanbehaviors','modifiers'] 
    
    for table in tableList: ##Create a bunch of empty dictionaries, with names from tableList
        fullDict[table] = {}
    
    currentDict = '' ##Used in the below "for" loop, to indicate which dictionary to add all the data
    for n,line in enumerate(allLines): ##Enumerating and adding n to allow the return of line numbers in case there's an error
        if len(line) == 1: ##Then the line should indicate the beginning of a new table.  Until a new table starts, all following lines should be added to the dictionary of this name.
            if line[0] not in tableList: ##Then there's a problem in the file
                print "Problem at line", (n+1), ":", line[0], " is not a recognized table name"
                fullDict = {} ##Empty the dictionary, to essentially halt any processes that may come after
                return fullDict 
            print 'Begin', line[0], 'dictionary.'
            currentDict = line[0]
        else: ##Line should be actual data to add to a table
            for x,item in enumerate(line): ##Check for numbers that are saved as strings
                if item.isdigit(): ##then item is a number and shouldn't stay a string
                    line[x] = int(item)
            fullDict[currentDict][line[0]] = line[1:] ##Set the first column of the data as the key, everything else as the value
            ##print 'Added', line[1:], "to", currentDict, 'with key #', line[0]
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

def writeInstance(dayTime, eventKey):
    '''
    Parses data for a line from the behavior_instances table and adds it together to a list.
    The list is joined into a string, presumably to write to the outFile.
    dayTime is a datetime object and represents the date and time of the instance.
    eventKey is an integer and is the key for the "instances" dictionary corresponding to the instance.
    Returns the string that can be written to the outFile.
    '''
    global allData, neighborAbbrev, instances_modifiers, foodsLong, foodsShort, observer
    outList = [] ##List of strings that will be joined together
    ##observer = allData['observers'][(allData['behaviorinstances'][eventKey][9])][2]
    ##outList.append(observer.upper())
    eventTypeID =  allData['behaviors'][(allData['behaviorinstances'][eventKey][1])][7] ##Look up behavior type id
    eventType = allData['behaviortypes'][eventTypeID][1] ##Using behavior type id, get the actual abbrev for that behavior type
    if eventType == 'proximity': ##Then it's a "neighbor" line. Let's use a shorter abbreviation.
        eventType = neighborAbbrev
    outList.append(eventType.upper()) ##Add code to indicate what kind of line this is
    outList.append(observer.upper())
    outList.append(dayTime.date().isoformat())  ##Add date  
    outList.append(dayTime.time().isoformat()) ##then time
    actorID = allData['individuals'][(allData['behaviorinstances'][eventKey][0])][1] ##Get actor
    outList.append(actorID.upper())
    actID = allData['behaviors'][(allData['behaviorinstances'][eventKey][1])][1]  ##Get act
    outList.append(actID.upper())
    if allData['behaviorinstances'][eventKey][2] == '': ##There's no actee. We don't want to pass '' to the "indivs" dictionary
        acteeID = 'NULL'
    else:
        acteeID = str(allData['individuals'][(allData['behaviorinstances'][eventKey][2])][1]) ##Convert to string in case the actee is 997, 998
    outList.append(acteeID.upper())
    if eventKey in instances_modifiers: ##then there was a modifier recorded with this event as well
        modKey = instances_modifiers[eventKey] ##Get the modifiers ID
        modifier = allData['modifiers'][modKey][1] ##Get the modifier (a string)
        if modifier.upper() in foodsLong: ##Then the modifier is a food, and we want to change it to its abbreviation.
            foodIndex = foodsLong.index(modifier.upper())
            print ("Replacing food code '" + modifier + "' with '" + foodsShort[foodIndex] + "'")
            modifier = foodsShort[foodIndex] ##Replace the long food name with its short name
        outList.append(modifier.upper())
    outLine = '\t'.join(outList)
    print outLine
    return str(outLine + '\n')

def writeFocalFollow(dayTime, eventKey):
    '''
    Parses data for a line from the focalfollows table and adds it together to a list.
    The list is joined into a string, presumably to write to the outFile.
    dayTime is a datetime object and represents the date and time of the focal follow.
    eventKey is an integer and is the key for the "focalfollows" dictionary corresponding to the focal.
    Returns the string that can be written to the outFile.
    '''
    global allData, focalAbbrev, groupsLong, groupsShort, observer
    outList = [] ##List of strings that will be joined together
    outList.append(focalAbbrev.upper()) ##Add code to indicate that this line begins a new focal sample
    outList.append(observer.upper())
    outList.append(dayTime.date().isoformat())  ##Add date  
    outList.append(dayTime.time().isoformat()) ##then time
    focalGrpID = allData['individuals'][(allData['focalfollows'][eventKey][0])][4] ##Get group ID number, based on the residence of the focal individual
    focalGrpName = (allData['groups'][focalGrpID][0])  ##Get group name
    if focalGrpName.upper() in groupsLong: ##This _should_ be always true
        grpIndex = groupsLong.index(focalGrpName.upper())
        print ("Replacing group name '" + focalGrpName + "' with '" + groupsShort[grpIndex] + "'")
        focalGrpName = groupsShort[grpIndex]
    outList.append(focalGrpName.upper())
    focalID = allData['individuals'][(allData['focalfollows'][eventKey][0])][1]
    outList.append(focalID.upper())
    focDuration = allData['focalfollows'][eventKey][5]
    focDurDelta = timedelta(0,focDuration)
    endTime = dayTime + focDurDelta
    outList.append(endTime.time().isoformat())
    outLine = '\t'.join(outList)
    print outLine
    return str(outLine + '\n')

def writeAdLib(dayTime, eventKey):
    '''
    Parses data for a line from the adlibs table and adds it together to a list.
    The list is joined into a string, presumably to write to the outFile.
    dayTime is a datetime object and represents the date and time of the note.
    eventKey is an integer and is the key for the "adlibs" dictionary corresponding to the note.
    Returns the string that can be written to the outFile.
    '''
    global allData, observer, noteAbbrev
    outList = [] ##List of strings that will be joined together
    outList.append(noteAbbrev.upper()) ##Add code to indicate that this line is a free-form text note
    outList.append(observer.upper())
    outList.append(dayTime.date().isoformat())  ##Add date  
    outList.append(dayTime.time().isoformat()) ##then time
    outList.append(allData['adlib'][eventKey][-1])
    outLine = '\t'.join(outList)
    print outLine
    return str(outLine + '\n')

def writeAll(outputFile, eventList):
    '''
    Reads the sorted (date/time, event dictionary name, event key) tuples in eventList, converts them to readable text, then writes the text to outputFile.
    Assumes outputFile is already open for writing.
    Returns a message, ideally to print to the console, that the process is complete.
    '''
    global allData, observer, prim8Version
    eventList.sort() ##Should be sorted already, but just in case
    outLine = 'Parsed data from AmboPrim8, version ' + str(prim8Version)+'\n' ##Start every file with this line 
    outputFile.write(outLine)
    for (eventDayTime, eventTable, tableKey) in eventList:
        if eventTable == 'behaviorinstances':
            outLine = writeInstance(eventDayTime, tableKey)
            outputFile.write(outLine)
        elif eventTable == 'focalfollows':
            outLine = writeFocalFollow(eventDayTime, tableKey)
            outputFile.write(outLine)
        elif eventTable == 'adlib':
            outLine = writeAdLib(eventDayTime, tableKey)
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
    observers=[] ##List of all observers who recorded the data.  Ideally, it's just one observer and could thus just be a string, but let's leave it flexible.
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

    ##Populate the observers list
    for i in allData['observers'].itervalues():
        if i[-1] != 'initials':
            observers.append(i[-1].upper())
    
    ##In case more than one observer, separate their initials with a comma
    observer = ','.join(observers)

    ##Get the food codes, so we can note the short name, not the long one.
    foodsLong, foodsShort = getCodes(open('./foodcodes.txt','r'), 1, 0)

    ##Get a corrected list of group names, because prim8 doesn't comprehend group names with apostrophes. E.g. we want "ACA", not "acacia".  Prim8 can't handle "acacia's".
    groupsLong, groupsShort = getCodes(open('./groupcodes.txt', 'r'), 3, 2)

    print "Creating export file"
    ##outPath = asksaveasfilename(defaultextension='.txt', title='Name of the exported data file?')
    outFile = open(outPath, 'w')
    ##outFile = open('./../output_test.txt','w')
    
    ##Let's finally output something!
    print writeAll(outFile, noteList)

    print "Closing export file at", outPath
    outFile.close()