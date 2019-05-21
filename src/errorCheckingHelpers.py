'''
Created on 6 Aug 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''
from babaseWriteHelpers import isType

def behaviorsInNote(dataLine, criteriaBehavs):
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
    
    All legitimate names used as actor or actee should be exactly 3 characters,
    so any names that aren't will be flagged here, whether or not they were
    specifically listed as possible "placeholder" values beforehand.
    
    This function is different from checkNeighborNotReal in that it uses a
    different (larger) set of "placeholder" values.  Some of these values are
    okay for use as neighbors.  See Babase documentation.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of lists of strings: the lines where this is true.
    '''
    from constants import unknSnames, unnamedCodes, adlibAbbrev
    
    # Make a set of known "placeholder" codes to check for 
    plcHoldrs = set(unknSnames.keys()).union(unnamedCodes)
    
    linesOfInterest = [line for line in dataLines if isType(line, adlibAbbrev)]
    
    return [line for line in linesOfInterest if line[5] in plcHoldrs or line[7] in plcHoldrs or len(line[5]) <> 3 or len(line[7]) <> 3]

def checkActorIsActee(dataLines):
    '''
    Checks ad-lib and neighbor lines in dataLines for cases where the two
    indicated individuals are the same. 
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of lists of strings: the lines where this is true.
    '''
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
    
    from constants import focalAbbrev
    
    allFocals = [line for line in dataLines if isType(line, focalAbbrev)]
    overlapHdrs = []
    
    for focal in allFocals:
        allOverlaps = findOverlaps(focal, allFocals)
        for overlap in allOverlaps:
            overlapHdrs.append((focal,overlap))
    return overlapHdrs

def checkInvalidFocalTypes(dataLines):
    '''
    Checks all focal header lines for invalid focal sample types.  These will
    occur, for example, if an observer accidentally starts a focal on an adult
    male.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of lists of strings: the lines where this is true.
    '''
    from constants import focalAbbrev, stypeAdultFem, stypeJuv
    
    focals = [line for line in dataLines if isType(line, focalAbbrev)]
    
    return [focal for focal in focals if focal[6] not in [stypeAdultFem, stypeJuv]]

def checkMountsConsortsDuringFocal(dataLines):
    '''
    Checks if mounts, ejaculations, and consorts were recorded during a focal 
    sample. Returns a list of list of strings representing all the cases that
    were outside a focal sample.
    
    Checks both "note" lines and "ad-lib" lines for these behaviors.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split. [0] in each list of strings is the "type" of data
    recorded in that line.
    '''
    from constants import focalAbbrev, noteAbbrev, adlibAbbrev, bb_consort, bb_mount, bb_ejaculation
    from datetime import datetime
    
    mountsEtc = [bb_consort, bb_mount, bb_ejaculation]
    outLines = []
    lastFocal = []
    focalEnd = ''
    
    for line in dataLines:
        if isType(line, focalAbbrev):
            lastFocal = line[:]
            focalEnd = ' '.join([lastFocal[2], lastFocal[7]])
            focalEnd = datetime.strptime(focalEnd, '%Y-%m-%d %H:%M:%S')
        
        # Check for behaviors in notes
        elif isType(line, noteAbbrev) and behaviorsInNote(line, mountsEtc):
            if len(lastFocal) == 0: # no focal yet
                outLines.append(line)
            elif not duringFocal(line, focalEnd):
                outLines.append(line)

        # Check for behaviors in ad-libs
        elif isType(line, adlibAbbrev) and line[6] in mountsEtc:
            if len(lastFocal) == 0: # no focal yet
                outLines.append(line)
            elif not duringFocal(line, focalEnd):
                outLines.append(line)
    
    return outLines

def checkMountsConsortsInvolvedFocal(dataLines):
    '''
    Checks data for cases where a mount, ejaculation, or consort was recorded
    and makes sure either the actor or actee was the focal individual. Returns a
    list of list of strings representing all the cases where this is true.
    
    Checks both "note" lines and "ad-lib" lines for these behaviors.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split. [0] in each list of strings is the "type" of data
    recorded in that line.
    '''
    from constants import focalAbbrev, noteAbbrev, adlibAbbrev, bb_consort, bb_mount, bb_ejaculation
    
    mountsEtc = [bb_consort, bb_mount, bb_ejaculation]
    outLines = []
    lastFocal = []
    focalIndiv = ''
    
    # Gather lines of interest
    for line in dataLines:
        if isType(line, focalAbbrev):
            lastFocal = line[:]
            focalIndiv = lastFocal[5].upper()

        elif isType(line, noteAbbrev) and behaviorsInNote(line, mountsEtc):
            if focalIndiv == '': # no focal yet
                outLines.append(line)
                continue
            interaction = (line[-1]).split() # SHOULD be [actor, act, actee]
            if interaction[1].upper() in mountsEtc: # this is an admittedly poor attempt to parse actor/actee from a note
                actor = interaction[0].upper()
                actee = interaction[2].upper()
                if focalIndiv not in [actor, actee]:
                    outLines.append(line)

        elif isType(line, adlibAbbrev) and line[6] in mountsEtc:
            if focalIndiv == '': # no focal yet
                outLines.append(line)
            else:
                actor = line[5]
                actee = line[7]
                if focalIndiv not in [actor, actee]:
                    outLines.append(line)
    
    return outLines

def checkNeighborNotReal(dataLines):
    '''
    Checks neighbor lines in dataLines for cases where the neighbor is noted as
    "INF" (a not-yet-named infant) or some other placeholder-type value.
    
    All legitimate names used as a neighbor should be exactly 3 characters, so
    any names that aren't will be flagged here, whether or not they were
    specifically listed as possible "placeholder" values beforehand.
    
    This function is different from checkActorActeeNotReal in that it uses a
    different (smaller) set of "placeholder" values.  Some of values used as
    neighbors are not allowed for use in ad-libs.  See Babase documentation.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of lists of strings: the lines where this is true.
    '''
    from constants import unnamedCodes, neighborAbbrev
    
    # Make a set of known "placeholder" codes to check for 
    plcHoldrs = set(unnamedCodes)
    
    linesOfInterest = [line for line in dataLines if isType(line, neighborAbbrev)]
    
    return [line for line in linesOfInterest if line[5] in plcHoldrs or line[7] in plcHoldrs or len(line[5]) <> 3 or len(line[7]) <> 3]

def checkNeighborsPerPoint(dataLines):
    '''
    Counts the number of neighbor lines for each "point" line in dataLines.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of (point, number of neighbors) tuples.  The "point" is a 
    string: the items from a "point" list of strings joined and tab-delimited.
    The "number of neighbors" is an integer.
    '''
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
    from constants import focalAbbrev, noteAbbrev
    
    focalDates = set()
    notes = []
    
    for line in dataLines:
        if isType(line, focalAbbrev):
            focalDates.add(line[2]) # Add the focal date
        elif isType(line, noteAbbrev):
            notes.append(line)
    
    return [note for note in notes if note[2] not in focalDates]

def checkPointMatchesFocal(dataLines):
    '''
    Checks data in dataLines for "point" lines where the indicated focal
    individual doesn't match the "current" focal individual and/or their dates
    don't match.  "Current", meaning the individual listed in the most-recent
    same-day focal header.  Includes any "point" lines where there is no most-
    recent same-day focal header.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a list of list of strings: the "point" lines that don't match the
    current focal.
    '''
    from constants import focalAbbrev, pntAbbrev
    
    lastFocal = []
    nonMatchingPoints = []
    
    for line in dataLines:
        if isType(line, focalAbbrev):
            lastFocal = line[:]
        elif isType(line, pntAbbrev):
            if lastFocal == []: #PNT with no HDR yet, report this
                nonMatchingPoints.append(line)
            elif not sameActor(lastFocal, line) or not sameDate(lastFocal, line):
                nonMatchingPoints.append(line)

    return nonMatchingPoints    

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

def checkTooManyPoints(dataLines):
    '''
    Checks the data in dataLines for focals with more than 10 points.  Does not
    count points that don't match the focal.
    
    The idea is to find samples where the observer recorded too many points.  If
    too many points appear to have been recorded, but there's an obvious
    alternate explanation (besides the observer simply recording too many), we
    don't want the problem reported here.
    
    Returns a list of (Focal header as string, integer number of points) tuples.
    '''
    tooManyPoints = []
    
    nonMatchingPoints = checkPointMatchesFocal(dataLines)
    theData = [line for line in dataLines if line not in nonMatchingPoints]
    focalsDict = getPointsPerFocal(theData)
    
    for (focal, points) in sorted(focalsDict.items()):
        if len(points) > 10:
            tooManyPoints.append((focal, len(points)))
    
    return tooManyPoints    

def checkUniqueNeighbors(dataLines, sampleProtocols):
    '''
    Checks all the recorded neighbors for each point collected during
    sampleProtocols samples to make sure that the list of neighbors is unique.
    Ideally, only check juvenile samples because the adult female protocol
    allows for some redundancy.  Returns a list of lists of strings: the point
    lines that have non-unique neighbors, and all of the point's associated
    neighbor lines.
    
    When considering uniqueness of neighbors, placeholder names (any names in
    constants.unknSnames) are ignored.
    
    dataLines is a list of lists of strings, presumed to be all the data from a
    file, stripped and split. sampleProtocols is a list of strings.
    '''
    from constants import unknSnames, focalAbbrev, pntAbbrev, neighborAbbrev
    
    # Make placeholders for iteration.
    # Holds the last-read "header" line, but only for focals of the type(s) allowed by sampleProtocols
    currentHeader = []
    #Holds the last-read "point" line, but only if it was in an allowed focal 
    currentPoint = []
    
    # Dictionary of points and neighbors.
    myPnts = {}
    #   Key: the point line--joined as a string
    #   Value: list of the neighbor lines (as lists of strings) for the point
    
    # Key for dictionary when neighbors are missing a point line
    missingPntKey = '(MISSING POINT LINE)'
    myPnts[missingPntKey] = []
    
    for line in dataLines:
        if line[0] not in [focalAbbrev, pntAbbrev, neighborAbbrev]:
            # Then we don't care about it for this question
            continue
        elif isType(line, focalAbbrev):
            if line[6] in sampleProtocols: #This is a focal sample of interest
                currentHeader = line[:]
                currentPoint = []
            else: #We don't care about any of the data in this focal
                currentHeader = []
                currentPoint = []
                continue
        # All that's left are points and neighbors. If currentHeader is empty, then we don't care about any of these.
        elif currentHeader == []:
            continue
        # Only points and neighbors that actually happened during focals of interest are left
        elif isType(line, pntAbbrev):
            if sameDate(line, currentHeader): #This should always be true, but added here just in case
                currentPoint = line[:]
                myPnts['\t'.join(currentPoint)] = []
        elif isType(line, neighborAbbrev):
            if currentPoint == []: #This should only happen if the observer messed up somewhere else
                myPnts[missingPntKey].append(line)
            elif sameDate(line, currentPoint):
                myPnts['\t'.join(currentPoint)].append(line)
    
    # Get list of names that are allowed to be nonunique
    fakeNames = unknSnames.keys()
    
    # Make list to hold the point and neighbor lines with nonunique neighbors
    nonUniqueNeighbors = []
    
    for (point, neighbors) in myPnts.iteritems():
        nghNames = []
        for neighbor in neighbors: #Collect all the neighbor names into one list
            if neighbor[7] not in fakeNames:
                nghNames.append(neighbor[7])
        if len(nghNames) > len(set(nghNames)): #Then 1 or more neighbors is redundant
            if len(nonUniqueNeighbors) > 0: # For every instance after the first, add a newline first
                nonUniqueNeighbors.append([]) # When this is output to file, a newline will be added
            nonUniqueNeighbors.append(point.split('\t'))
            for neighbor in neighbors:
                nonUniqueNeighbors.append(neighbor)

    return nonUniqueNeighbors

def countFocalTypes(dataLines):
    '''
    Counts the number of lines in dataLines that are focal headers, grouped by
    focal sample type (juvenile, adult female, or other).
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.
    
    Returns a dictionary whose keys are all the focal sample types that occur in
    the data, and whose values are the number of times those lines occur.
    '''
    from constants import focalAbbrev, stypeAdultFem, stypeJuv, stypeOther
    
    allFocals = [line for line in dataLines if isType(line, focalAbbrev)]
    
    focalTypes = [stypeAdultFem, stypeJuv]
    
    focalsDict = {}
    focalsDict[stypeAdultFem] = 0
    focalsDict[stypeJuv] = 0
    focalsDict[stypeOther] = 0
    
    for focal in allFocals:
        if focal[6] in focalTypes:
            focalsDict[focal[6]] += 1
        else:
            focalsDict[stypeOther] += 1
    
    # Remove the "other" stype from the dictionary if it's zero. It SHOULD
    # always be zero, so it's only noteworthy when it's > 0.
    
    if focalsDict[stypeOther] == 0:
        focalsDict.pop(stypeOther)
    
    return focalsDict

def countLines(dataLines, sampleType=''):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split. sampleType is a string indicating which "type" of
    data to count in dataLines.
    
    Counts the number of lines in dataLines are of "type" sampleType. If
    sampleType is not provided or is the empty string, counts all lines.
    
    Returns an integer, the number of lines.
    '''
    
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

def countSummary(dataLines):
    '''
    Reads the data in dataLines and counts the number of lines of each type that
    occur in the data.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  A code indicating the sample's "type" should be
    at [0] in each line.
    
    Returns a dictionary whose keys are all the line types that occur in the
    data, and whose values are the number of times those lines occur.
    '''
    countDict = {}
    
    for line in dataLines:
        if line[0] in countDict.keys():
            countDict[line[0]] += 1
        else:
            countDict[line[0]] = 1
    
    return countDict

def countUniqueDates(dataLines):
    '''
    Reads the data in dataLines and counts the number of unique dates that occur
    in the data.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  The date should be in position [2] of each line.
    
    Returns an integer: the number of distinct dates that occur in the data.
    '''
    theDates = set()
    
    for line in dataLines:
        thisDate = line[2]
        theDates.add(thisDate)
    
    return len(theDates)

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

def getPointsPerFocal(dataLines):
    '''
    Gathers the "point" lines recorded during each focal sample. Returns a
    dictionary whose keys are focal headers (each a single string), and whose
    values are lists of associated points (each its own list of strings).
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  They are also presumed to be in chronological
    order.
    '''
    from constants import focalAbbrev, pntAbbrev
    
    focalCounts = {}
    lastFocal = 'NONE YET'
    focalCounts[lastFocal] = []
    
    for line in dataLines:
        if isType(line, focalAbbrev):
            lastFocal = '\t'.join(line)
            focalCounts[lastFocal] = []
        elif isType(line, pntAbbrev):
            focalCounts[lastFocal].append(line)
    
    return focalCounts

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
    
    oosLines =[line for line in dataLines if isType(line, pntAbbrev) and line[6] == outOfSightValue]
    
    return oosLines

def sameActor(eventLine1, eventLine2):
    '''
    Checks if the actor/focal individual in both lines is the same.
    
    Parameters are lists of strings, presumed to be lines of data, split and
    stripped.  Index [5] of both lists should be the "actor", or dominant/focal
    individual in the observation.
        For focal headers, and "point" and "neighbor" lines, this will be the
        focal individual.  For interactions, this will be the "actor".
    
    Returns TRUE or FALSE.
    '''
    
    indiv1 = eventLine1[5]
    indiv2 = eventLine2[5]
    return indiv1 == indiv2

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

def theseWithoutThose(dataLines, thisType, notThose, butYesThem = [], beforeThem = []):
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
    
    If the optional "beforeThem" is given, then add the qualification that there
    also mustn't be any "notThose" lines before lines of the type(s) included in
    "beforeThem".  For example, given "theData" below (slightly different from above):
        1 HDR datadatadatadata
        2 PNT datadatadatadata
        3 HDR datadatadatadata
        4 NGH datadatadatadata
        5 PNT datadatadatadata
        6 NGH datadatadatadata
        7 HDR datadatadatadata
    
        theseWithoutThose(theData, 'PNT', ['NGH'], beforeThem = ['HDR']) would
        return line 2
        
        theseWithoutThose(theData, 'PNT', ['NGH']) would return
        nothing
        
        theseWithoutThose(theData, 'HDR', ['PNT'], ['NGH'],['PNT']) would return
        line 3 (it's essentially asking for HDR with NGH before any PNT)
    
    
    dataLines is a list of lists of strings, presumed to be all the data from a
    file, stripped and split. [0] in each list of strings is the "type" of data
    recorded in that line.
    
    thisType is a string, indicating which line types to check for. notThose
    is a list of strings indicating which line types can't follow thisType
    lines. butYesThem is also a list of strings.
    
    thisType and any items in butYesThem cannot be in notThose.
    
    Returns a list of lists of strings.
    '''
    
    if thisType in notThose:
        return ['ERROR (' + thisType + ': Cannot exclude an item type from itself']
    for this in butYesThem:
        if this in notThose:
            return ['ERROR (' + this + '): Cannot require and forbid an item type'] 
    
    these = []
    maybeThis = []
    yesFound = False
    
    checkYes = False
    if len(butYesThem) > 0:
        checkYes = True
    
    for line in dataLines:
        if maybeThis == []:
            if isType(line, thisType):
                maybeThis = line[:]
                if checkYes:
                    yesFound = False
        else: #maybeThis is not empty, so there's a candidate for "these"
            if checkYes:
                if line[0] in beforeThem: # When checkYes, notThose can be in beforeThem, so check beforeThem first
                    if yesFound: # Hooray!
                        these.append(maybeThis)
                    maybeThis = []
                    yesFound = False
                elif line[0] in notThose: # maybeThis is a "these" but not "without those"
                    maybeThis = []
                    yesFound = False
                elif line[0] in butYesThem: #found a "butYesThem"
                    yesFound = True
                elif isType(line, thisType):
                    if yesFound: # Winner!
                        these.append(maybeThis)
            
            else:
                if line[0] in notThose: # maybeThis is a "these" but not "without those"
                    maybeThis = []
                    
                elif isType(line, thisType) or line[0] in beforeThem: # maybeThis didn't have any of "notThose"
                    these.append(maybeThis)
                    
                    maybeThis = []
                    if isType(line, thisType):
                        maybeThis = line[:]
    
    if maybeThis != []: # we have a maybeThis and got to end of data without finding any of "those". Add it. Unless...
        if checkYes and not yesFound: # Made it to end, but no yesFound. Don't add.
            pass
        else:
            these.append(maybeThis)
    
    return these

def writeAlert(checkFor, alertData, showSpecifics = True, numForAlert = ''):
    '''
    Writes a message indicating that a condition was checked, then shows how
    many times the condition occurred and (if desired) recites the lines in the
    data where it occurred (the alertData). The condition is not actually
    checked in this function; this is just for making human-friendly output.
    
    The boolean "showSpecifics" allows the option to choose whether or not the
    data in alertData are included in the output.
    
    Often, the number of times an event occurred will simply be the length of
    alertData.  In case that's not accurate, the number can instead be provided
    in "numForAlert".
    
    Returns a single string that will likely contain one or more newlines.  It
    is of the format:
        '(checkFor):\t[number of cases]
        \talertData[0]
        ...
        \talertData[n]'
    
    When showSpecifics is False, only the first line in the above example is
    output.
    
    checkFor is a string indicating in human language what was checked.
    
    alertData is a list of strings, and may be empty. If non-empty, each string
    will be written as an example case of the condition described in checkFor.
    '''
    if numForAlert == '':
        numForAlert = len(alertData)
    
    resultInfo = []
    commentLine = checkFor + ':\t' + str(numForAlert)
    resultInfo.append(commentLine)
    
    if showSpecifics:
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