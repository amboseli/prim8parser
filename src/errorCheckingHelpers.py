'''
Created on 6 Aug 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''
def behaviorsInNote (dataLine, criteriaBehavs):
    '''
    Checks the data at the end of dataLine (the string at [-1]) to see if any of
    the behaviors in criteriaBehavs (a list of strings) occur as space-delimited
    substrings (case-insensitive).  Returns True if yes, False if no.
    
    For example, given this dataLine:
        ['TXT', 'AAA', '1944-06-06', '12:34:56', 'A busy day today']
        
            behaviorsInNote(dataLine, ['a'])  is True, because 'a' occurs by
            itself, not part of a larger word
            behaviorsInNote(dataLine, ['b']) is False, because although 'b' does
            occur, it's not its own word
    '''
    theNote = dataLine[-1].split()
    theNote = [item.upper() for item in theNote]
    
    for behav in criteriaBehavs:
        if behav.upper() in theNote:
            return True
    
    return False

def checkActorActeeNotReal(dataLines):
    '''
    Checks ad-lib lines in dataLines for cases where either the actor or actee
    is noted as "NULL" or some other placeholder-type value.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of lists of strings: the lines where this is true.
    '''
    from babaseWriteHelpers import isType
    from constants import unknSnames, unnamedCodes, adlibAbbrev
    
    # Make a set of known "placeholder" codes to check for 
    plcHoldrs = set(unknSnames.keys()).union(unnamedCodes)
    
    linesOfInterest = [line for line in dataLines if isType(line, adlibAbbrev)]
    
    return [line for line in linesOfInterest if line[5] in plcHoldrs or line[7] in plcHoldrs]

def checkActorIsActee(dataLines):
    '''
    Checks ad-lib and neighbor lines in dataLines for cases where the two
    indicated individuals are the same. 
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of lists of strings: the lines where this is true.
    '''
    from babaseWriteHelpers import isType
    from constants import adlibAbbrev, neighborAbbrev
    
    linesOfInterest = [line for line in dataLines if isType(line, adlibAbbrev) or isType(line, neighborAbbrev)]
    
    return [line for line in linesOfInterest if line[5] == line[7]]

def checkBehavsInNotes(dataLines, criteriaBehavs):
    '''
    Checks all "note" lines for cases where any of the behaviors in
    criteriaBehavs occur.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of lists of strings: the lines where this is true.
    '''
    from babaseWriteHelpers import isType
    from constants import noteAbbrev
    
    notes = [line for line in dataLines if isType(line, noteAbbrev)]
    
    return [note for note in notes if behaviorsInNote(note, criteriaBehavs)]

def checkDuplicateFocals(dataLines):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  The following are assumed true about the lists of
    strings:
        1) The line "type" is indicated by the string at [0]
        2) The date for event is at [2]
        3) For lines indicating a new focal sample, the focal's ID is at [5]
    
    Gathers all the lines indicating the beginning of new focal samples, and
    checks for cases where the same individual was sampled more than once in the
    same day.
    
    Returns a list of (date, name) tuples (date and name are both strings),
    sorted by date, listing all duplicate focals. If none found, returns an
    empty list.
    '''
    from constants import focalAbbrev
    from babaseWriteHelpers import isType
    
    # Make list of (date, name) tuples for each focal sample
    dateNames = [(line[2],line[5]) for line in dataLines if isType(line, focalAbbrev)]
    
    duplicateFocals = set() 
    for focal in dateNames:
        if dateNames.count(focal) > 1:
            duplicateFocals.add(focal)
    
    if len(duplicateFocals) > 0: # Then we have some duplicates
        return sorted(list(duplicateFocals), key = lambda focal: focal[0])

    return []

def checkDuplicateGroups(dataLines):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  The following are assumed true about the lists of
    strings:
        1) The line "type" is indicated by the string at [0]
        2) The date for event is at [2]
        3) For lines indicating a new focal sample, the focal group is at [4]
    
    Gathers all the lines indicating the beginning of new focal samples, and
    checks for cases where more than one group was sampled on a single day.
    
    Returns a list of (date, groups) tuples (date and groups are both strings),
    sorted by date, listing all duplicates. If none found, returns an empty
    list.
    '''
    from constants import focalAbbrev
    from babaseWriteHelpers import isType
    
    # Make set of (date, group) tuples from all the data
    focalInfoSet = set([(line[2], line[4]) for line in dataLines if isType(line, focalAbbrev)])
    
    # Dictionary of dates (keys) and list of group(s) (values) sampled on those dates
    datesGroups = {}
    
    for (focalDate, focalGrp) in focalInfoSet:
        if focalDate not in datesGroups:
            datesGroups[focalDate] = [focalGrp]
        else:
            datesGroups[focalDate].append(focalGrp)
            
    duplicateFocals = []
    
    for (focalDate, groups) in sorted(datesGroups.items(), key = lambda pair: pair[0]): # Sort by date
        if len(groups) > 1:
            duplicateFocals.append((focalDate, str(groups)))            
    
    return duplicateFocals

def checkFocalOverlaps(dataLines):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split. [0] in each list of strings is the "type" of data
    recorded in that line.
    
    Checks for overlapping focals in dataLines, and returns a list of
    (focal1, focal2) tuples. focal1 and 2 are both lists of strings.
        focal1 is a "header" line, focal2 is the "header" of the last focal to
        occur during focal1
    '''
    from babaseWriteHelpers import isType
    from constants import focalAbbrev
    
    allFocals = [line for line in dataLines if isType(line, focalAbbrev)]
    overlapHdrs = []
    
    for focal in allFocals:
        allOverlaps = findOverlaps(focal, allFocals)
        for overlap in allOverlaps:
            overlapHdrs.append((focal,overlap))
    return overlapHdrs

def checkNeighborsPerPoint(dataLines):
    '''
    Counts the number of neighbor lines for each "point" line in dataLines.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of (point, number of neighbors) tuples.  The "point" is a 
    string: the items from a "point" list of strings joined and tab-delimited.
    The "number of neighbors" is an integer.
    '''
    from babaseWriteHelpers import isType
    from constants import pntAbbrev, neighborAbbrev
    
    lastPoint = 'NONE YET'
    pointsAndCounts = {}
    pointsAndCounts[lastPoint[:]] = 0
    
    for line in dataLines:
        if isType(line, pntAbbrev):
            lastPoint = '\t'.join(line)
            pointsAndCounts[lastPoint[:]] = 0
        elif isType(line, neighborAbbrev):
            pointsAndCounts[lastPoint[:]] += 1
    
    return sorted(pointsAndCounts.items(), key = lambda pair: pair[0])

def checkNotesNoFocals(dataLines):
    '''
    Checks data in dataLines for "note" lines on days with no focal samples
    recorded.  This is important, because these notes will not be recorded
    in Babase.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of list of strings: the "note" lines on days with no focals.
    '''
    from babaseWriteHelpers import isType
    from constants import focalAbbrev, noteAbbrev
    
    focalDates = set()
    notes = []
    
    for line in dataLines:
        if isType(line, focalAbbrev):
            focalDates.add(line[2]) # Add the focal date
        elif isType(line, noteAbbrev):
            notes.append(line)
    
    return [note for note in notes if note[2] not in focalDates]

def checkSpecificBehavior(dataLines, specBehaviors):
    '''
    Check each line in dataLines to see if the "behavior" in that line (if any)
    is in specBehaviors (list of strings).
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of lists of strings: each line that does have the specific
    behavior(s).
    '''
    from babaseWriteHelpers import checkIfBehavior
    
    return [line for line in dataLines if len(line)>=7 and checkIfBehavior(line, specBehaviors) ]

def countLines(dataLines, sampleType=''):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split. sampleType is a string indicating which "type" of
    data to count in dataLines.
    
    Counts the number of lines in dataLines are of "type" sampleType. If
    sampleType is not provided or is the empty string, counts all lines.
    
    Returns an integer, the number of lines.
    '''
    from babaseWriteHelpers import isType
    
    if sampleType == '':
        return len(dataLines)
    
    return len([line for line in dataLines if isType(line, sampleType)])

def countLinesPerDay(dataLines, sampleType=''):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split. sampleType is a string indicating which "type" of
    data to count in dataLines.  Each line's date should be at [2].
    
    Gets all distinct dates from the data in dataLines, then notes how many
    lines of "type" sampleType occurred each day. If sampleType is not provided
    or is the empty string, counts all lines.
    
    Returns a single string that will include several line breaks.
    '''
    from babaseWriteHelpers import isType
    
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
            
    # Write the results
    resultInfo = []
    commentLine = sampleType + ' Lines Collected Per Day:'
    resultInfo.append(commentLine)
    
    for (date, count) in sorted(dateCounts.items(), key = lambda pair: pair[0]):
        commentLine = '\t' + date + ':\t' + str(count)
        resultInfo.append(commentLine)
    
    return '\n'.join(resultInfo)

def dataSummary(dataLines):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  Each list of strings should have a 'yyyy-mm-dd'
    date at [2], and a hh:mm:ss time at [3]. A code indicating the sample's
    "type" should be at [0].
    
    Reads the data in dataLines and provides summary information about it.
    Doesn't check for errors, only factual information:
        -- First and Last day/time of data
        -- Number of lines/events recorded of any type
        -- Number of lines/events recorded of each type
        -- # of focals/day

    Returns a single string that will include several line breaks.
    '''
    from constants import focalAbbrev, neighborAbbrev, noteAbbrev, adlibAbbrev, pntAbbrev
    
    summaryLines = []
    
    # Add summary header
    commentLine = '------General summary of data:\n'
    summaryLines.append(commentLine)
    
    # Add first and last day/time
    firstTime, lastTime = firstAndLastLines(dataLines)
    commentLine = 'Data begins ' + firstTime + ' and ends ' + lastTime
    summaryLines.append(commentLine)
    
    # Count lines and line types
    typesToCheck = ['', focalAbbrev, pntAbbrev, neighborAbbrev, adlibAbbrev, noteAbbrev]
    for item in typesToCheck:
        numLinesAsStr = str(countLines(dataLines, item))
        displayItem = item[:]
        if displayItem == '':
            displayItem = 'all'
        commentLine = 'Number of ' + displayItem + ' lines:\t\t' + numLinesAsStr
        summaryLines.append(commentLine)
    
    # Add line break
    summaryLines.append('\n')
    
    # Daily breakdown of focals collected
    commentLine = countLinesPerDay(dataLines, focalAbbrev)
    summaryLines.append(commentLine)
    
    return '\n'.join(summaryLines)

def duringFocal (eventLine, focalEndTime):
    '''
    Checks if the day/time in eventLine is before the focalEndTime.
    eventLine is a list of strings. The date is at eventLine[2], the time is at eventLine[3].
    focalEndTime is a datetime, not just a time.
    Returns TRUE or FALSE.
    '''
    from datetime import datetime
    
    eventDayTime = ' '.join(eventLine[2:4])
    eventDateTime = datetime.strptime(eventDayTime, '%Y-%m-%d %H:%M:%S')
    return eventDateTime < focalEndTime

def errorAlertSummary(dataLines):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  Each list of strings should have a 'yyyy-mm-dd'
    date at [2], and a hh:mm:ss time at [3]. A code indicating the sample's
    "type" should be at [0].
    
    Reads the data in dataLines and lists cases of apparent errors in the data.
    Also brings alerts to things that may not be "wrong" but may indicate
    problems:
        -- Same focal collected more than once/day
        -- More than 1 group sampled in a single day
        -- Focals with overlapping times
        -- Focals with no data at all
        -- Focals with no points
        -- Points w/ no neighbors (exclude out of sight points)
        -- Neighbors w/o a preceding PNT
        -- Points w/ >3 neighbors
        -- Neighbors w/o an N0/N1/N2 code
        -- Notes on days w/o any focals
        -- Actor == Actee
        -- Actor or Actee is a non-sname placeholder (NULL, XXX, 998, etc.)
        -- Notes lines possibly containing mounts, ejaculations, or consorts
        -- Non-note lines that recorded mounts, ejaculations, or consorts
        
        Not implemented, but maybe worth adding:
        -- JM's AS/OS/DSing AF's
        -- Actor/actee in different groups
    
    Returns a single string that will include several line breaks.
    '''
    from babaseWriteHelpers import isType
    from constants import focalAbbrev, pntAbbrev, neighborAbbrev, noteAbbrev, adlibAbbrev, outOfSightValue, p8_nghcodes, bb_mount, bb_ejaculation, bb_consort
    
    alertLines = []

    # Add summary header
    commentLine = '------Alerts and Errors:\n'
    alertLines.append(commentLine)
    
    # Check for individuals sampled >1x/day
    alertData = ['\t'.join(line) for line in checkDuplicateFocals(dataLines)]
    commentLine = writeAlert('duplicate (date, sname) pairs', alertData) + '\n'
    alertLines.append(commentLine)

    # Check for >1 group sampled in one day
    alertData = ['\t'.join(line) for line in checkDuplicateGroups(dataLines)]
    commentLine = writeAlert('>1 group sampled in a day', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for overlapping focals
    alertData = []
    allOverlaps = checkFocalOverlaps(dataLines)
    for (focal1, focal2) in allOverlaps:
        outFocal1 = ' '.join([focal1[2], focal1[3], focal1[5]]) # Date, time, ID
        outFocal2 = ' '.join([focal2[2], focal2[3], focal2[5]])
        alertData.append(', '.join([outFocal1, outFocal2]))
    commentLine = writeAlert('overlapping focals', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for focal samples with no data
    alertData = ['\t'.join(line) for line in theseWithoutThose(dataLines, focalAbbrev, [pntAbbrev, neighborAbbrev, noteAbbrev, adlibAbbrev])]
    commentLine = writeAlert('focal samples with no data', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for focal samples with no points
    alertData = ['\t'.join(line) for line in theseWithoutThose(dataLines, focalAbbrev, [pntAbbrev])]
    commentLine = writeAlert('focal samples without points', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for in-sight points with no neighbors
    alertData = theseWithoutThose(dataLines, pntAbbrev, [neighborAbbrev])
    alertData = ['\t'.join(line) for line in alertData if line[6] != outOfSightValue]
    commentLine = writeAlert('in-sight points w/o neighbors', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for neighbors without a preceding point. This occurs in two
    # different ways: Neighbor lines occur just after a focal starts and before
    # any points, or a point is followed by >3 neighbors
    
    # First, neighbors after focals
    alertData = theseWithoutThose(dataLines, focalAbbrev, [pntAbbrev], [neighborAbbrev])
    alertData = ['\t'.join(line) for line in alertData]
    commentLine = writeAlert(('header-then-neighbor, with no ' + pntAbbrev), alertData) +'\n'
    alertLines.append(commentLine)
    
    # Second, points with >3 neighbors
    alertData = [pair[0] for pair in checkNeighborsPerPoint(dataLines) if pair[1] > 3]
    commentLine = writeAlert('points with >3 neighbors', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for neighbors without appropriate neighbor codes
    alertData = ['\t'.join(line) for line in dataLines if isType(line, neighborAbbrev) and line[-1] not in p8_nghcodes]
    commentLine = writeAlert('neighbors w/o neighbor codes', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for notes on days without any focals
    alertData = ['\t'.join(line) for line in checkNotesNoFocals(dataLines)]
    commentLine = writeAlert('notes on days without any focals', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for data where actor is actee, or focal is neighbor
    alertData = ['\t'.join(line) for line in checkActorIsActee(dataLines)]
    commentLine = writeAlert('lines where actor is actee, or focal is neighbor', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for data where actor or actee is a non-sname placeholder
    alertData = ['\t'.join(line) for line in checkActorActeeNotReal(dataLines)]
    commentLine = writeAlert('lines where actor or actee is a non-sname placeholder', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for notes that appear to contain mounts, ejaculations, or consorts
    MEC_list = [bb_mount, bb_ejaculation, bb_consort]
    alertData = ['\t'.join(line) for line in checkBehavsInNotes(dataLines, MEC_list)]
    commentLine = writeAlert('notes that appear to contain mounts, ejaculations, or consorts', alertData) + '\n'
    alertLines.append(commentLine)
    
    # Check for lines with mounts, ejaculations, or consorts recorded as regular, legit behaviors
    alertData = ['\t'.join(line) for line in checkSpecificBehavior(dataLines, MEC_list)]
    commentLine = writeAlert('lines with mounts, ejaculations, or consorts recorded as regular, legit behaviors', alertData) + '\n'
    alertLines.append(commentLine)
    
    return '\n'.join(alertLines)

def findOverlaps(thisHdrLine, otherHdrs):
    '''
    thishdrLine is a list of strings, a "header" line indicating a new focal
    sample.
    
    otherHdrs is a list of lists of strings. These are all the "header" lines.
    
    Checks if any headers in otherHdrs begin before hdrLine ended. Returns a
    list of lists of strings: any overlapping headers from otherHdrs, or an
    empty list if no overlaps.
    '''
    thisHdrBegin = getDateTime(thisHdrLine, 2, 3)
    thisHdrEnd = getDateTime(thisHdrLine, 2, -1)
    overLaps = []
    
    for hdr in otherHdrs:
        otherHdrBegin = getDateTime(hdr, 2, 3)
        if otherHdrBegin > thisHdrBegin and otherHdrBegin < thisHdrEnd:
            overLaps.append(hdr)
    
    return overLaps

def firstAndLastLines(dataLines):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  Each list of strings should have a 'yyyy-mm-dd'
    date at [2], and a hh:mm:ss time at [3].
    
    Returns two strings, both formatted 'yyyy-mm-dd hh:mm:ss' and representing
    the first and last events in dataLines.
    '''
    #Make sure the data are in chronological order
    srtLines = sorted(dataLines, key = lambda line: (line[2], line[3]))
    
    firstEvent = getDateTime(srtLines[0], 2, 3).strftime('%Y-%m-%d %H:%M:%S')
    lastEvent = getDateTime(srtLines[-1], 2, 3).strftime('%Y-%m-%d %H:%M:%S')
    
    return (firstEvent, lastEvent)
    
def getDateTime(eventLine, dateIndex, timeIndex):
    '''
    Given a list of strings (eventLine) with a yyyy-mm-dd date at [dateIndex] and the hh:mm:ss time at [timeIndex].
    Returns a datetime object with the date and time from eventLine.
    '''
    from datetime import datetime
    
    joinedTime = ' '.join([eventLine[dateIndex],eventLine[timeIndex]]) ##Result should be string 'yyyy-mm-dd hh:mm:ss'
    return datetime.strptime(joinedTime, '%Y-%m-%d %H:%M:%S')

def pointsOutOfSight(dataLines):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  [0] in each list of strings is the "type" of data
    recorded in that line. In "point" lines, [6] is the point's "activity", or
    "out of sight".
    
    Searches through the data for "out of sight" points and gathers them into a
    list.
    
    Returns a list of lists of strings: all the "out of sight" lines.
    '''
    from constants import pntAbbrev, outOfSightValue
    from babaseWriteHelpers import isType
    
    oosLines =[line for line in dataLines if isType(line, pntAbbrev) and line[6] == outOfSightValue]
    
    return oosLines

def sameDate(eventLine1, eventLine2):
    '''
    Parameters are lists of strings, presumed to be lines of data, split and stripped.
        All that really matters, though, is [2] of both parameters is a yyyy-mm-dd date.
        
    Checks if the date in both lines is the same.
    
    Returns TRUE or FALSE.
    '''
    from datetime import datetime
    
    date1 = datetime.strptime(eventLine1[2],'%Y-%m-%d')
    date2 = datetime.strptime(eventLine2[2],'%Y-%m-%d')
    return date1 == date2

def theseWithoutThose(dataLines, thisType, notThose, butYesThem = []):
    '''
    Checks the data in dataLines and collects lines of "type" thisType that
    don't have any notThose lines after them before the next thisType line.
    For example, in the data below:
        1 HDR datadatadatadata
        2 PNT datadatadatadata
        3 HDR datadatadatadata
        4 HDR datadatadatadata
        5 PNT datadatadatadata
        6 NGH datadatadatadata
    
        theseWithoutThose(theData, HDR, [PNT]) would not return line 1 or 4
        because a PNT line occurs before the next HDR or before the end of data.
        Only line 3 would be returned.
        
        theseWithoutThose(theData, PNT, [NGH]) would return line 2 but not 5.
        
    If the optional "butYesThem" is given, then also add the qualification that
    at least one line of at least one type in butYesThem must also occur before
    the next "thisType" line. For example given "theData" above:
        
        theseWithoutThose(theData, HDR, [PNT], [NGH]) would return no lines.
        
        theseWithoutThose(theData, HDR, [NGH], [PNT]) would return only line 1.
    
    dataLines is a list of lists of strings, presumed to be all the data from a
    file, stripped and split. [0] in each list of strings is the "type" of data
    recorded in that line.
    
    thisType is a string, indicating which line types to check for. notThose
    is a list of strings indicating which line types can't follow thisType
    lines. butYesThem is also a list of strings.
    
    thisType and any items in butYesThem cannot be in notThose.
    
    Returns a list of lists of strings.
    '''    
    from babaseWriteHelpers import isType
    
    if thisType in notThose:
        return ['ERROR (' + thisType + ': Cannot exclude an item type from itself']
    for this in butYesThem:
        if this in notThose:
            return ['ERROR (' + this + '): Cannot require and forbid an item type'] 
    
    these = []
    maybeYes = []
    yesFound = False
    
    checkYes = False
    if len(butYesThem) > 0:
        checkYes = True
    
    for line in dataLines:
        if maybeYes == []:
            if isType(line, thisType):
                maybeYes = line[:]
                if checkYes:
                    yesFound = False
        else: #maybeYes is not empty, so there's a candidate for "these"
            if line[0] in notThose: # maybeYes is a "these" but not "without those"
                maybeYes = []
                if checkYes:
                    yesFound = False
            elif checkYes and line[0] in butYesThem: #found a "butYesThem"
                yesFound = True
            elif isType(line, thisType): # maybeYes didn't have any of "notThose"
                if checkYes and not yesFound: #maybeYes didn't have any of "butYesThem"
                    pass
                else:
                    these.append(maybeYes)
                maybeYes = line[:]
    
    if maybeYes != []: # we have a maybeYes and got to end of data without finding any of "those". Add it.
        these.append(maybeYes)
    
    return these

def writeAlert(checkFor, alertData):
    '''
    Writes a message indicating that a condition was checked, then recites cases
    in the data that meet that condition. The condition is not actually checked
    in this function; this is just for making human-friendly output.
    
    Returns a single string that will contain one or more newlines.  It is of
    the format:
        'Check for (checkFor): [NONE/FOUND]
        \talertData[0]
        ...
        \talertData[n]'
    
    The first line will end with "NONE" if len(alertData) is 0, otherwise
    "FOUND".
    
    checkFor is a string indicating in human language what was checked.
    
    alertData is a list of strings, and may be empty. If non-empty, each string
    will be written as an example case of the condition described in checkFor.
    '''
    resultFlag = 'NONE'
    
    if len(alertData) > 0:
        resultFlag = 'FOUND'
    
    resultInfo = []
    commentLine = 'Check for ' + checkFor + ': ' + resultFlag
    resultInfo.append(commentLine)
    
    for item in alertData:
        commentLine = '\t' + item
        resultInfo.append(commentLine)
    
    return '\n'.join(resultInfo)
    

def writeHeader(aFilePath):
    '''
    aFilePath is a string and should be the path to the file being checked for
    errors.
    
    Creates a "header" message for the beginning of an error-check analysis,
    using the format:
        "[Today's date/time yyyy-mm-dd hh:mm:ss] analysis of file [filename]"
    
    Returns a string: the header itself.
    '''
    from os import path
    from datetime import datetime
    
    fileName = path.basename(aFilePath)
    thisTime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    return thisTime + ' analysis of file: ' + fileName