'''
Created on 28 Oct 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''
from compareFocalLogs import *
from errorCheckingHelpers import *
from constants import textBoundary
from os import path

def dataSummary(dataLines, doDailyFocals = True):
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
        -- # of focals/day (if doDailyFocals is True)

    Returns a single string that will include several line breaks.
    '''
    
    summaryLines = []
    
    # Add summary header
    commentLine = '------General summary of data:\n'
    summaryLines.append(commentLine)
    
    # Add first and last day/time
    firstTime, lastTime = firstAndLastLines(dataLines)
    commentLine = 'Data begins ' + firstTime + ' and ends ' + lastTime
    summaryLines.append(commentLine)
    
    # Count lines and line types
    commentLine = 'Total number of lines:\t\t' + str(countLines(dataLines))
    summaryLines.append(commentLine)
    
    typeCounts = countSummary(dataLines)
    focalTypes = countFocalTypes(dataLines)
    
    typesToCheck = [focalAbbrev, pntAbbrev, neighborAbbrev, adlibAbbrev, noteAbbrev]
    for item in typesToCheck:
        numItemsAsString = str(typeCounts.get(item, 0))
        commentLine = 'Number of ' + item + ' lines:\t\t' + numItemsAsString
        summaryLines.append(commentLine)
        # After number of focals, break it down by type
        if item == focalAbbrev:
            for (stype, count) in sorted(focalTypes.items()):
                commentLine = '\t\t\t\t' + stype + ':\t\t' + str(count)
                summaryLines.append(commentLine)
    uniqueDates = countUniqueDates(dataLines)
    commentLine = 'Number of sampling dates:\t\t' + str(uniqueDates)
    summaryLines.append(commentLine)
    
    # Add line break
    summaryLines.append('\n')
    
    if doDailyFocals:
        # Daily breakdown of focals collected
        commentLine = countLinesPerDay(dataLines, focalAbbrev)
        summaryLines.append(commentLine)
    
    return '\n'.join(summaryLines)

def errorAlertSummary(dataLines, focalLogPath = "", showSpecifics = True):
    '''
    Reads the data in dataLines and lists cases of apparent errors in the data.
    Also brings alerts to things that may not be "wrong" but may indicate
    problems:
        -- Same focal collected more than once/day
        -- More than 1 group sampled in a single day
        -- Focals with overlapping times
        -- Focals w/ invalid focal type
        -- Focals with no data at all
        -- Focals with no points
        -- Points with date/focal individual different from the current focal sample
        -- Focals with >10 points
        -- Points w/ no neighbors (exclude out of sight points)
        -- Neighbors w/o a preceding PNT
        -- Points w/ >3 neighbors
        -- Points from juvenile samples with non-unique neighbors
        -- Neighbors w/o an N0/N1/N2 code
        -- Notes on days w/o any focals
        -- Actor == Actee
        -- Actor or Actee is a non-sname placeholder (NULL, XXX, 998, etc.)
        -- Neighbor is a non-sname placeholder ('IMM', 'INF')
        -- Focal samples that were not logged (if focalLogPath provided)
        -- Logged (as completed) samples that were not done (if focalLogPath provided)
        -- Notes lines possibly containing mounts, ejaculations, or consorts
        -- Non-note lines that recorded mounts, ejaculations, or consorts
        -- Mounts/Ejaculations/Consorts not during a focal
        -- Mounts/Ejaculations/Consorts not involving the focal individual
        
        Not implemented, but maybe worth adding:
        -- JM's AS/OS/DSing AF's
        -- Actor/actee in different groups
    
    The boolean "showSpecifics" allows the option to choose whether (True) or
    not (False) the actual data that elicited each alert/error should be
    included in the output.
    
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  Each list of strings should have a 'yyyy-mm-dd'
    date at [2], and a hh:mm:ss time at [3]. A code indicating the sample's
    "type" should be at [0].
    
    Returns a single string that will include several line breaks.
    '''    
    alertLines = []

    # Add summary header
    commentLine = '------Alerts and Errors:\n'
    alertLines.append(commentLine)
    
    # Check for individuals sampled >1x/day
    alertData = ['\t'.join(line) for line in checkDuplicateFocals(dataLines)]
    commentLine = writeAlert('Duplicate (date, sname) pairs', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)

    # Check for >1 group sampled in one day
    alertData = ['\t'.join(line) for line in checkDuplicateGroups(dataLines)]
    commentLine = writeAlert('>1 group sampled in a day', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for overlapping focals
    alertData = []
    allOverlaps = checkFocalOverlaps(dataLines)
    for (focal1, focal2) in allOverlaps:
        outFocal1 = ' '.join([focal1[2], focal1[3], focal1[5]]) # Date, time, ID
        outFocal2 = ' '.join([focal2[2], focal2[3], focal2[5]])
        alertData.append(', '.join([outFocal1, outFocal2]))
    commentLine = writeAlert('Overlapping focals', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for focals w/ invalid focal type
    alertData = ['\t'.join(line) for line in checkInvalidFocalTypes(dataLines)]
    commentLine = writeAlert('Focal samples with invalid focal type', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for focal samples with no data
    alertData = ['\t'.join(line) for line in theseWithoutThose(dataLines, focalAbbrev, [pntAbbrev, neighborAbbrev, noteAbbrev, adlibAbbrev])]
    commentLine = writeAlert('Focal samples with no data', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for focal samples with no points
    alertData = ['\t'.join(line) for line in theseWithoutThose(dataLines, focalAbbrev, [pntAbbrev])]
    commentLine = writeAlert('Focal samples without points', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for points that don't match the current focal
    # Set aside the list of these points, because they will be referred-to again later
    nonMatchingPoints = ['\t'.join(line) for line in checkPointMatchesFocal(dataLines)]
    alertData = nonMatchingPoints[:]
    commentLine = writeAlert("Points that don't match (or have) a current focal", alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for focal samples with >10 points
    alertData = [(focal + '; ' + str(count) + ' points') for (focal, count) in checkTooManyPoints(dataLines)]
    commentLine = writeAlert('Focal samples with > 10 points', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for in-sight points with no neighbors
    alertData = theseWithoutThose(dataLines, pntAbbrev, [neighborAbbrev], beforeThem = [focalAbbrev])
    alertData = ['\t'.join(line) for line in alertData if line[6] != outOfSightValue] #Exclude out-of-sight points
    alertData = [line for line in alertData if line not in nonMatchingPoints] #Exclude non-matching points
    commentLine = writeAlert('In-sight points w/o neighbors', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for neighbors without a preceding point. This occurs in two
    # different ways: Neighbor lines occur just after a focal starts and before
    # any points, or a point is followed by >3 neighbors
    
    # First, neighbors after focals
    alertData = theseWithoutThose(dataLines, focalAbbrev, [pntAbbrev], [neighborAbbrev], [pntAbbrev])
    alertData = ['\t'.join(line) for line in alertData]
    commentLine = writeAlert(('Header-then-neighbor, with no ' + pntAbbrev), alertData, showSpecifics) +'\n'
    alertLines.append(commentLine)
    
    # Second, points with >3 neighbors
    alertData = [pair[0] for pair in checkNeighborsPerPoint(dataLines) if pair[1] > 3]
    commentLine = writeAlert('Points with >3 neighbors', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for non-unique neighbors in juvenile samples
    alertData = checkUniqueNeighbors(dataLines, [stypeJuv])
    numForAlert = len([line for line in alertData if len(line) > 0 and isType(line, pntAbbrev)])
    alertData = ['\t'.join(line) for line in alertData]
    commentLine = writeAlert('Non-unique neighbors in juvenile samples', alertData, showSpecifics, numForAlert) + '\n'
    alertLines.append(commentLine)
        
    # Check for neighbors without appropriate neighbor codes
    alertData = ['\t'.join(line) for line in dataLines if isType(line, neighborAbbrev) and line[-1] not in p8_nghcodes]
    commentLine = writeAlert('Neighbors w/o neighbor codes', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for notes on days without any focals
    alertData = ['\t'.join(line) for line in checkNotesNoFocals(dataLines)]
    commentLine = writeAlert('Notes on days without any focals', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for data where actor is actee, or focal is neighbor
    alertData = ['\t'.join(line) for line in checkActorIsActee(dataLines)]
    commentLine = writeAlert('Actor is actee, or focal is neighbor', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for data where actor or actee is a non-sname placeholder
    alertData = ['\t'.join(line) for line in checkActorActeeNotReal(dataLines)]
    commentLine = writeAlert('Actor or actee is a non-sname placeholder', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for lines where neighbor is a non-sname placeholder (different placeholders from ad-libs)
    alertData = ['\t'.join(line) for line in checkNeighborNotReal(dataLines)]
    commentLine = writeAlert('Neighbor is a non-sname placeholder', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for focals done that aren't in the log (if provided)
    if focalLogPath <> "":
        # Then a log was provided. Do this check.
        alertData = getFocalsNotLogged(dataLines, focalLogPath)
        alertData = [line[0]+"\t"+line[2]+" point(s) in sight, out of "+line[1] for line in alertData]
        commentLine = writeAlert("Focal samples that aren't in the log", alertData, showSpecifics) + '\n'
        alertLines.append(commentLine)
    
    # Check for logged (as complete) focals that aren't in the data
    if focalLogPath <> "":
        # Then a log was provided. Do this check.
        alertData = getLoggedNotDone(dataLines, focalLogPath)
        commentLine = writeAlert("Logged samples that aren't in the data", alertData, showSpecifics) + '\n'
        alertLines.append(commentLine)
    
    # Check for notes that appear to contain mounts, ejaculations, or consorts
    MEC_list = [bb_mount, bb_ejaculation, bb_consort, bb_mount_long, bb_ejaculation_long, bb_consort_long, bb_consort_long2]
    alertData = ['\t'.join(line) for line in checkBehavsInNotes(dataLines, MEC_list)]
    commentLine = writeAlert('Notes that appear to contain mounts, ejaculations, or consorts', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for lines with mounts, ejaculations, or consorts recorded as regular, legit behaviors
    alertData = ['\t'.join(line) for line in checkSpecificBehavior(dataLines, MEC_list)]
    commentLine = writeAlert('Mounts, ejaculations, or consorts recorded as regular, legit behaviors', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for lines with mounts, ejaculations, or consorts recorded outside of a focal sample
    alertData = ['\t'.join(line) for line in checkMountsConsortsDuringFocal(dataLines)]
    commentLine = writeAlert('Mounts, ejaculations, or consorts recorded outside of a focal sample', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for lines with mounts, ejaculations, or consorts not involving the focal individual
    alertData = ['\t'.join(line) for line in checkMountsConsortsInvolvedFocal(dataLines)]
    commentLine = writeAlert('Mounts, ejaculations, or consorts not involving the focal individual', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    return '\n'.join(alertLines)

def errorCheck (inFilePath, outFilePath, focalLogPath = ""):
    '''
    Checks the data in the file at inFilePath for possible errors.
    Also does some counting of basic statistics about the data, e.g. (how many focals, how many adlibs, etc.)
    Errors, alerts, and statistics will be written to the file at outFilePath.
        If outFilePath already existed, everything already there will be
        retained. New data will be added to the top, followed by what was
        already there.
    focalLogPath is the (optional) path to a focal sample log, which will allow a few additional kinds of checks to occur.
    Prints a message that the process is complete.
    Returns nothing.
    '''
    # Check if previous summary exists
    prevData = [] # To hold previous data, if any
    if path.isfile(outFilePath):
        print "Getting previous data from:", path.basename(outFilePath) 
        outFile = open(outFilePath,'rU')
        prevData = outFile.readlines()
        outFile.close()
    
    print "Creating export file:", path.basename(outFilePath) 
    outFile = open(outFilePath,'w')
    
    outMsg = writeHeader(inFilePath) 
    outFile.write(outMsg + '\n\n')
    
    print "Opening import file:", path.basename(inFilePath)
    impFile = open(inFilePath, 'rU')
    impEvents = impFile.readlines()
    impFile.close()
       
    print "Adding all lines to allEvents list"
    allEvents =  [line.strip().split('\t') for line in impEvents] ##List of all lines read from the import file (impFile)
    allEvents.pop(0) ##Remove the "Parsed data..." line at the top
    
    print "Getting data summary"
    outMsg = dataSummary(allEvents)
    outFile.write(outMsg + '\n\n')
    
    print "Getting errors and alerts summary"
    outMsg = errorAlertSummary(allEvents, focalLogPath, showSpecifics=True)
    outFile.write(outMsg + '\n')

    if len(prevData) > 0:
        outMsg = textBoundary + textBoundary
        outFile.write(outMsg + '\n')
        outFile.writelines(prevData)

    print "Closing export file"
    outFile.close()
    outMsg = "Finished checking data in " + path.basename(inFilePath)
    print outMsg

#if __name__ == '__main__':
    
    #impPath = askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='Select a processed prim8 file:')
#    impPath = './../output_test.txt'

    #outPath = asksaveasfilename(defaultextension='.txt', title='Name for the error summary file?')
#    outPath = './../file_summary.txt'
    
#    errorCheck(impPath, outPath)
