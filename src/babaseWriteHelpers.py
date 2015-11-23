'''
Created on 28 Sep 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

Functions used to interpret data in preparation for their import to Babase.
'''

def isType(dataLine, sampleType):
    '''
    dataLine is a list of strings, representing one line tab-delimited data.
    sampleType is a string that indicates what "type" of data this function is checking for.
    
    Returns True if sampleType is the first item in dataLine.  Otherwise, False.
    '''
    return dataLine[0] == sampleType

def checkIfBehavior(dataLine, ifBehavs):
    '''
    Checks if the behavior in the given line of data is a member of the string list ifBehavs.
    
    Returns True if in the list, False if not.  Also returns False if dataLine doesn't have enough fields to check a behavior.
    '''
    # Make sure dataLine has a behavior field to check
    if len(dataLine) < 7:
        print "Can't check for invalid behaviors, line is too short:", dataLine
        return True
    
    return dataLine[6] in ifBehavs

def countMins(dataLines):
    '''
    dataLines is a list of lists of strings, presumably the result of a "readlines" from a data file
        followed by a "strip()" and a "split()".
    
    Because point samples are supposed to be collected once per minute, the number of points collected
        is sometimes called the number of "minutes" recorded.  Hence "countMins", because it's counting 
        minutes.
    
    Returns a dictionary whose keys are the "header" lines indicating a new focal sample, and whose values
        are the number of "point" lines recorded after that header and before the next one.
        
        WARNING: As of this writing (28 Sep 2015), AmboPrim8's ability to accurately note the "end" of a focal sample is
            unreliable.  For this and other reasons, this function does not use duration of the focal to 
            count "minutes". With the Psion devices that we previously used, the number of "point" lines 
            was used for this measure anyway, so we'll stick with that even when focal sample end times do
            become reliable.  AmboPrim8 doesn't allow recording of "point" lines unless there is a current
            focal, so this isn't an issue.  The logic used herein will not work for most other types, e.g.
            ad-libs/all-occurrences, which may be recorded at the end of a day for hours after the end of
            focal sampling.
             
    '''
    from constants import focalAbbrev, pntAbbrev
    
    numMins = {}
    lastFocal = ''
    
    for line in dataLines:
        if isType(line, focalAbbrev):
            joinedLine = '\t'.join(line)
            numMins[joinedLine] = 0
            lastFocal = joinedLine[:]
        elif isType(line, pntAbbrev):
            numMins[lastFocal] += 1
    
    return numMins

def collectTxtNotes(dataLines):
    '''
    dataLines is a list of lists of strings, presumably the result of a "readlines" from a data file
        followed by a "strip()" and a "split()".
    
    Gathers all text notes in dataLines and determines which focal (also from dataLines) each note belongs
        to.  In Babase, text notes must be associated with a specific focal sample.  Prim8 does not require
        this, so notes may not actually be recorded during the focal. A note is associated with a focal if:
        1) The note is during the focal, or
        2) The note is on the same day as the focal and the focal is the last recorded before the note, or
        3) The note is on the same day as the focal and the focal is the first recorded after the note.
        Notes recorded on days with no focals recorded won't be associated with any focal.

    Returns a dictionary: its keys are each focal "HDR" line (string, not list). Its values are lists of
        associated notes, saved as lists of strings.  So a value is a list of lists of strings. It may be
        an empty list.
    '''
    from constants import focalAbbrev, noteAbbrev
    from errorCheckingHelpers import sameDate
    
    focalNotes ={}
    
    theData = [line for line in dataLines if line[0] in [focalAbbrev, noteAbbrev]]
    
    # Probably not necessary, but just in case let's sort by date, time
    theData.sort(key = lambda line: (line[2], line[3]))
    
    #Initialize variables to use in the loop
    orphanNotes = [] #Temporary container for notes that aren't during or after a focal
    lastFocal = [] 
    
    # First group together all notes that happened during or after a focal
    for line in theData:
        if isType(line, focalAbbrev):
            lastFocal = line[:]
            focalNotes['\t'.join(line)] = []
        elif isType(line, noteAbbrev):
            if lastFocal == [] or not sameDate(line, lastFocal):
                orphanNotes.append(line)
            else: # The note in "line" must be after a focal that occurred on the same day
                focalNotes['\t'.join(lastFocal)].append(line)
    
    # Now take care of the "orphans". Find the first focal on the same day as the note
    for note in orphanNotes:
        for line in theData:
            if isType(line, focalAbbrev) and sameDate(note, line):
                focalNotes['\t'.join(line)].append(note)
                break # Stop looping through all of the data. We only want the first focal.
    
    return focalNotes

def neighborIsNull(dataLine):
    '''
    dataLine is a list of strings that represents a single line of data.
        It should only ever be a "neighbor" line.
        
    Checks if the neighbor is actually a code that means NULL or "no neighbor".
        These lines are recorded in Prim8, but are not added to Babase.
        
    Returns True if the neighbor is NULL or a "no neighbor" code. False otherwise.
    '''
    from constants import unknSnames, emptyAbbrev
    
    neighborID = dataLine[7]
    
    return unknSnames.get(neighborID, neighborID) == emptyAbbrev

def getNCode(sampleType, neighborCode):
    '''
    sampleType is a string that indicates a sampling protocol.
    neighborCode is a string, a code from the Prim8 data that indicates which kind of neighbor.
    
    Translates the Prim8 neighbor code into the Babase neighbor code.
    
    Returns a string: the "ncode" used in Babase, or the given neighborCode if no "ncode" is found.
    '''
    from constants import neighborsFem, neighborsJuv, stypeJuv
    
    ncodes = neighborsFem
    
    if sampleType == stypeJuv:
        ncodes = neighborsJuv
    
    return ncodes.get(neighborCode, neighborCode)

def getPointActs(dataLine):
    '''
    dataLine is a list of strings that represents a single line of data.
        It should only ever be a "point" sample.
        
    Splits the activity/position[/kidposition/kidsuckling] string into a list of strings.
        If the activity indicates feeding, checks for the presence of a food code.
    
    Returns a two-object tuple: 
        1) the list of strings representing the activity (and so on)
        2) the food code, if found.  Empty string if not found.  A string either way. 
    '''
    from constants import focalFeeding
    behavior = dataLine[6]
    allCodes = [item for item in behavior]
    foodcode = ''
    if allCodes[0] == focalFeeding:
        foodcode = dataLine[-1]
    return allCodes, foodcode

def getProgramSetup(dataStrLine):
    '''
    dataStrLine is a string that should be the first line of a processed Prim8 data file. 
    Its format is presumed to be:
        "Parsed data from: PROGRAMID, SETUPID, TABLETID"
        (e.g. "Parsed data from: AMBOPRIM8_1.150510, AMBOPRIM8_JUL15, Samsung Tablet A")
                
    Returns three strings: the program ID, then the setup ID, then the tablet ID
    '''
    dataList = dataStrLine.split(':',1) #Split only once in case there's a colon in one of the other fields for some reason
    dataList = dataList[1].split(',')
    dataList = [item.strip() for item in dataList]
    return dataList[0], dataList[1], dataList[2]

def behavDuringFocal(lastFocal, thisBehav):
    '''
    lastFocal is a list of strings, and should be a "header" line of data from a file.
        It may be an empty list, though.
    lastBehav is a list of strings, and should be an adlib/all-occurrences behavior line.
    
    After confirming that lastFocal is non-empty, checks if the time in thisBehav happened
        before the end of the focal sample in lastFocal.
        
    Returns True if thisBehav is recorded before lastFocal ended.  False otherwise.
    '''
    from errorCheckingHelpers import getDateTime, duringFocal
    
    if len(lastFocal) == 0:
        return False
    
    focalEnd = getDateTime(lastFocal, 2, 7)
    
    return duringFocal(thisBehav, focalEnd)

def transactionCommit(doCommit=True):
    '''
    doCommit is a boolean, and defaults to True.
    
    Returns the string that ends an SQL transaction. "COMMIT;" if True, "ROLLBACK;" if false.
    '''
    if doCommit:
        return "COMMIT;"
    return "ROLLBACK;"

def newFocal(dataLine, mins, prgID, setupID, tabletID):
    '''
    dataLine is a list of strings representing a single line read from the Prim8 data file.
        It should contain data about the beginning of a new focal sample.
        Its format is presumed to be:
        [data type, observer, date, begin time, group name, focal name, sample type, end time] (all strings) 
        (e.g. ["HDR", "SNS", "2015-09-22", "08:59:56", "ACA", "UJU", "JUV", "09:10:39"])
    prgID, setupID, and tabletID are strings representing specifics about the tablet and app used for 
        data collection.  Ideally, they're generated by the getProgramSetup function.
    
    Parses data from the line needed to write the SQL "insert" command.
    
    Returns a string: the SQL statement.
    '''
    from babaseSQL import insertSAMPLES_SQL, lookupGroupNum_SQL, lookupPalmtop_SQL, lookupProgramID_SQL, lookupSetupID_SQL
    from constants import stypesBabase
    
    date = dataLine[2]
    stime = dataLine[3]
    observer = dataLine[1]
    stype = stypesBabase.get(dataLine[6], dataLine[6])
    grp = lookupGroupNum_SQL(dataLine[4])
    sname = dataLine[5]
    programid = lookupProgramID_SQL(prgID)
    setupid = lookupSetupID_SQL(setupID)
    palmtop = lookupPalmtop_SQL(tabletID)
    
    return insertSAMPLES_SQL(date, stime, observer, stype, grp, sname, mins, programid, setupid, palmtop)

def newPoint(dataLine, pntMin):
    '''
    dataLine is a list of strings representing a single line read from the Prim8 data file.
        It should contain data about a new point sample.
    pntMin is an integer, and indicates the "point" or "minute" number.
        (e.g. the first point is 1, the second is 2, etc.)
    
    Parses data from the line needed to write the SQL "insert" command.
    
    If the "behavior" string is 4 characters long, it is interpreted as an adult female sample,
        and the additional data is inserted appropriately.
    
    Returns a string: the SQL statement.
    '''
    from babaseSQL import insertPOINT_DATA_SQL, insertFPOINTS_SQL
    
    ptime = dataLine[3]
    actCodes, foodcode = getPointActs(dataLine)
    activity = actCodes[0]
    posture = actCodes[1]
    
    if len(actCodes) == 4:
        kidcontact = actCodes[2]
        kidsuckle = actCodes[3]
        return insertPOINT_DATA_SQL(pntMin, activity, posture, ptime, foodcode) + insertFPOINTS_SQL(kidcontact, kidsuckle)
    
    return insertPOINT_DATA_SQL(pntMin, activity, posture, ptime, foodcode)

def newNeighbor(dataLine, currFocal):
    '''
    dataLine is a list of strings representing a single line read from the Prim8 data file.
        It should contain data about one of the focal's neighbors.
    currFocal is a list of strings representing the header of the current focal sample.
        It is used to determine the sample type, i.e. which sampling protocol was in use
        for this neighbor. This is important, because the significance of the ordering of
        neighbors varies between protocols.
    
    Parses data from the line needed to write the SQL "insert" command.
    
    Returns a string: the SQL statement.
    '''
    from babaseSQL import insertNEIGHBORS_SQL
        
    neighborID = dataLine[7]
    
    prim8NCode = dataLine[-1] # This is imperfect. If an ncode is omitted, then [-1] is the neighbor.
                                # It will return an error during import to Babase, so we'll leave this alone for now.
    sampleType = currFocal[6]
    babaseNCode = getNCode(sampleType, prim8NCode) 
    
    return insertNEIGHBORS_SQL(neighborID, babaseNCode)

def newInteraction(dataLine, lastFocal):
    '''
    Parses data from the line needed to write the SQL "insert" command.  lastFocal is used
        to determine if dataLine was recorded within lastFocal's duration.  If
        the line notes a behavior that we've designated as not okay for import
        to Babase, inserts it as a text note instead.
    
    dataLine is a list of strings representing a single line read from the Prim8 data file.
        It should contain data about an adlib/all-occurrences interaction.
    lastFocal is a list of strings representing the last focal sample begun before the event
        in dataLine. It may be empty.
    
    Returns a string: the SQL statement.
    '''
    from babaseSQL import insertACTOR_ACTEES_SQL
    from constants import saveAsNotes
    
    # Check if this interaction should be recorded as a note
    if checkIfBehavior(dataLine, saveAsNotes):
        return newNoteFromOther(dataLine)
    
    inFocal = behavDuringFocal(lastFocal, dataLine)
    observer = dataLine[1]
    date = dataLine[2]
    start = dataLine[3]
    actor = dataLine[5]
    act = dataLine[6]
    actee = dataLine[7]
    
    return insertACTOR_ACTEES_SQL(inFocal, observer, date, start, actor, act, actee)

def newNote(dataLine):
    '''
    Parses data from the line needed to write the SQL "insert" command. Because
    all text notes stored in Babase require it, adds a text "prefix" (one
    character) to the beginning of the note.  Also checks the text of the actual
    note for apostrophes, and adds an extra to ensure that the
    "single-quote" doesn't break any SQL.
    
    dataLine is a list of strings representing a single line read from the Prim8
    data file. It should contain data about a free-form text note.
                
    If the text of the note appears to be a consort, the text prefix will be the
    special code used for consorts. Otherwise, the usual prefix for
    miscellaneous/"other" notes will be used.

    Returns a string: the SQL statement.
    '''
    from babaseSQL import insertALLMISCS_SQL
    from constants import bb_consort, allMiscsPrefixConsort, allMiscsPrefixOther
    from errorCheckingHelpers import behaviorsInNote
    
    atime = dataLine[3]

    txtPrefix = allMiscsPrefixOther
    if behaviorsInNote(dataLine, [bb_consort]):
        txtPrefix = allMiscsPrefixConsort
    
    txt = (sqlizeApostrophes(dataLine[4])).upper()
    
    return insertALLMISCS_SQL(atime, txtPrefix, txt)    

def noteFromOther(dataLine):
    '''
    Takes the data from dataLine and rewrites it as a note line.  
    
    dataLine is a list of strings.
    
    Returns a list of strings.
    '''
    from constants import noteAbbrev
    
    newDataLine = dataLine[:4]
    newDataLine[0] = noteAbbrev
        
    noteText = ' '.join(dataLine[5:])
    newDataLine.append(noteText)
    
    return newDataLine

def newNoteFromOther(dataLine):
    '''
    Given a line of data, returns an SQL string to import that line as a text
    note instead of its original data type.
    '''
    correctedData = noteFromOther(dataLine)
    
    return newNote(correctedData)

def sqlizeApostrophes(someString):
    '''
    Checks a string for apostrophes (aka "single-quotes"). If found, replaces it
    with 2 of them. Returns the string with replacements made (if any).
    
    Used for strings that are meant to be added to a particular field in the
    database.  Without this, the single quotes in some note strings can
    prematurely end an SQL command.
    '''
    apost = "'"
    someString = someString.replace(apost, (apost+apost))
    return someString
