'''
Created 3 Jun 2019

Set of functions to generate periodic feedback forms for the observers.

This is a modified version of the "errorChecking" package. While the
"errorChecking" package is focused on providing useful information and
summaries for data management, this package is intended to provide
useful summaries and feedback for the observers who are actually
collecting the data. Because of this, some checks from errorChecking are
not performed here, and the text of some of the alerts is reworded.

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''
from compareFocalLogs import *
from errorCheckingHelpers import *
from constants import textBoundary
from os import path

def observerDataSummary(dataLines, doDailyFocals = True):
    '''
    dataLines is a list of list of strings, presumed to be all the data from a
    file, stripped and split.  Each list of strings should have a 'yyyy-mm-dd'
    date at [2], and a hh:mm:ss time at [3]. A code indicating the sample's
    "type" should be at [0].
    
    Reads the data in dataLines and provides summary information about it.
    Doesn't check for errors, only factual information:
        -- First and Last day/time of data
        -- Number of focal samples (HDRs) recorded
        -- # of focals/day (if doDailyFocals is True)
    Exactly which info is provided here is curated, because the full
    dump of data is probably more than our observers really need to
    see.

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
    
    typesToCheck = [focalAbbrev]
    for item in typesToCheck:
        numItemsAsString = str(typeCounts.get(item, 0))
        commentLine = 'Number of ' + item + ' lines:\t\t' + numItemsAsString
        summaryLines.append(commentLine)
    uniqueDates = countUniqueDates(dataLines)
    commentLine = 'Number of sample days:\t\t' + str(uniqueDates)
    summaryLines.append(commentLine)
    
    # Add line break
    summaryLines.append('\n')
    
    if doDailyFocals:
        # Daily breakdown of focals collected
        commentLine = countLinesPerDay(dataLines, focalAbbrev)
        summaryLines.append(commentLine)
    
    return '\n'.join(summaryLines)


def feedbackAlerts(dataLines, focalLogPath = "", showSpecifics = True):
    '''
    Reads the data in dataLines and lists cases of possible errors in
    the data that should be brought to the attention of the observers:  
        -- Focals with no points
        -- Focals with >10 points
        -- Points w/ no neighbors (exclude out of sight points)
        -- Points w/ >3 neighbors
        -- Points from juvenile samples with non-unique neighbors
        -- Actor == Actee
        -- Focal samples that were not logged (if focalLogPath provided)
        -- Logged (as completed) samples that were not done (if focalLogPath provided)
        
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
    commentLine = '------Alerts/Errors:\n'
    alertLines.append(commentLine)
    
    # Check for focal samples with no points
    alertData = ['\t'.join(line) for line in theseWithoutThose(dataLines, focalAbbrev, [pntAbbrev])]
    commentLine = writeAlert('Focal samples without points', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for focal samples with >10 points
    alertData = [(focal + '; ' + str(count) + ' points') for (focal, count) in checkTooManyPoints(dataLines)]
    commentLine = writeAlert('Focal samples with > 10 points', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for in-sight points with no neighbors
    nonMatchingPoints = ['\t'.join(line) for line in checkPointMatchesFocal(dataLines)] # To be excluded below
    alertData = theseWithoutThose(dataLines, pntAbbrev, [neighborAbbrev], beforeThem = [focalAbbrev])
    alertData = ['\t'.join(line) for line in alertData if line[6] != outOfSightValue] #Exclude out-of-sight points
    alertData = [line for line in alertData if line not in nonMatchingPoints] #Exclude non-matching points
    commentLine = writeAlert('In-sight points w/o neighbors', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
        
    # Second, points with >3 neighbors
    alertData = [pair[0] for pair in checkNeighborsPerPoint(dataLines) if pair[1] > 3]
    commentLine = writeAlert('Points with >3 neighbors', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for non-unique neighbors in juvenile samples
    alertData = checkUniqueNeighbors(dataLines, [stypeJuv])
    numForAlert = len([line for line in alertData if len(line) > 0 and isType(line, pntAbbrev)])
    alertData = ['\t'.join(line) for line in alertData]
    commentLine = writeAlert('Juvenile points with repeating neighbors (using adult female protocol for neighbors?)', alertData, showSpecifics, numForAlert) + '\n'
    alertLines.append(commentLine)
        
    # Check for data where actor is actee, or focal is neighbor
    alertData = ['\t'.join(line) for line in checkActorIsActee(dataLines)]
    commentLine = writeAlert('Individual interacted with itself, or focal is its own neighbor', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
        
    # Check for focals done that aren't in the log (if provided).
    # Exclude focals with no points.
    if focalLogPath <> "":
        # Then a log was provided. Do this check.
        alertData = getFocalsNotLogged(dataLines, focalLogPath)
        alertData = [line[0]+"\t"+line[2]+" point(s) in sight, out of "+line[1] for line in alertData if int(line[1]) > 0]
        commentLine = writeAlert("Focal samples that aren't in the log", alertData, showSpecifics) + '\n'
        alertLines.append(commentLine)
    
    # Check for logged (as complete) focals that aren't in the data
    if focalLogPath <> "":
        # Then a log was provided. Do this check.
        alertData = getLoggedNotDone(dataLines, focalLogPath)
        commentLine = writeAlert("Logged samples (with a check) that aren't in the data", alertData, showSpecifics) + '\n'
        alertLines.append(commentLine)
    
    return '\n'.join(alertLines)

def makeFeedback (inFilePath, outFilePath, focalLogPath = ""):
    '''
    Checks the data in the file at inFilePath for possible errors/alerts.
    Also does some counting of basic statistics about the data, e.g. (how many focals, how many adlibs, etc.)
    Errors, alerts, and statistics will be written to the file at outFilePath.
        UNLIKE the "errorChecking" function in errorChecking package,
        this function does not retain any pre-existing data from the
        file at outFilePath.
    focalLogPath is the (optional) path to a focal sample log, which will allow a few additional kinds of checks to occur.
    Prints a message that the process is complete.
    Returns nothing.
    '''    
    print "Creating export file:", path.basename(outFilePath) 
    outFile = open(outFilePath,'w')
    
    outMsg = writeHeader(inFilePath) 
    outFile.write(outMsg + '\n\n')
    
    print "Opening import file:", path.basename(inFilePath)
    impFile = open(inFilePath, 'rU')
    impFile.readline() ## Skip the header line
    allEvents = impFile.readlines()
    impFile.close()
    
    allEvents =  [line.strip().split('\t') for line in allEvents]
    
    print "Getting data summary"
    outMsg = observerDataSummary(allEvents)
    outFile.write(outMsg + '\n\n')
    
    print "Getting errors and alerts summary"
    outMsg = feedbackAlerts(allEvents, focalLogPath, showSpecifics=True)
    outFile.write(outMsg + '\n')

    print "Closing export file"
    outFile.close()
    outMsg = "Finished checking data in " + path.basename(inFilePath)
    print outMsg

