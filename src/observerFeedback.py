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
from constants import *
from compareFocalLogs import *
from errorCheckingHelpers import *
from feedbackHelpers import *
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
    firstTime = kenyaDateTime(firstTime, False)
    lastTime = kenyaDateTime(lastTime, False)
    commentLine = firstTime + ' - ' + lastTime
    summaryLines.append(commentLine)
    
    # Count lines and line types
    typeCounts = countSummary(dataLines)
    
    typesToCheck = {}
    typesToCheck[focalAbbrev] = 'sample'
    for item in sorted(typesToCheck.keys()):
        numItemsAsString = str(typeCounts.get(item, 0))
        commentLine = 'Number of ' + typesToCheck[item] + 's:\t\t' + numItemsAsString
        summaryLines.append(commentLine)
    uniqueDates = countUniqueDates(dataLines)
    commentLine = 'Number of sample days:\t' + str(uniqueDates)
    summaryLines.append(commentLine)
    
    # Add line break
    summaryLines.append('\n')
    
    if doDailyFocals:
        # Daily breakdown of focals collected
        commentLine = kenyaLinesPerDay(dataLines, focalAbbrev, 'Sample')
        summaryLines.append(commentLine)
    
    return '\n'.join(summaryLines)

def feedbackAlerts(dataLines, focalLogPath = "", showSpecifics = True):
    '''
    Reads the data in dataLines and lists cases of possible errors in
    the data that should be brought to the attention of the observers:  
        -- Focals with no points
        -- Focals with >10 points
        -- Points implying focal has an infant when she doesn't, and vice versa
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
    print("Begin feedbackAlerts. First row of dataLines is:")
    print(dataLines[0])
    
    alertLines = []

    # Add summary header
    commentLine = '------Alerts/Errors:\n'
    alertLines.append(commentLine)
    
    # Check for focal samples with no points
    print("Check for focal samples with no points")
    alertData = [kenyaFixLine(line) for line in theseWithoutThose(dataLines, focalAbbrev, [pntAbbrev])]
    alertData = ['\t'.join(line) for line in alertData]
    commentLine = writeAlert('Focal samples without points', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for focal samples with >10 points
    print("Check for focal samples with >10 points")
    alertData = []
    for (focal, count) in checkTooManyPoints(dataLines):
        focal = focal.strip().split('\t')
        focal = kenyaFixLine(focal)
        focal = '\t'.join(focal)
        alertData.append(focal + '; ' + str(count) + ' points')
    commentLine = writeAlert('Focal samples with more than 10 points', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Points implying focal has an infant when she doesn't, and vice versa
    # First, get a dictionary of moms and their kids
    moms = momsAndInfants("./momsAndInfants.txt")
    alertData = checkFocalInfantStatus(dataLines, moms)
    # Prune this a bit, so we can use the "kenyaFixLine" function.
    alertData = [line[0:7] + [line[-1]] for line in alertData]
    alertData = ['\t'.join(kenyaFixLine(line, True)) for line in alertData]
    commentLine = writeAlert("Points with infant when female has no infant, and vice versa", alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for in-sight points with no neighbors
    print("Check for in-sight points with no neighbors")
    alertData = theseWithoutThose(dataLines, pntAbbrev, [neighborAbbrev], beforeThem = [focalAbbrev])
    alertData = [line for line in alertData if line[6] != outOfSightValue] #Exclude out-of-sight points
    alertData = [line for line in alertData if line not in checkPointMatchesFocal(dataLines)] #Exclude non-matching points
    alertData = ['\t'.join(kenyaFixLine(line)) for line in alertData]
    commentLine = writeAlert('Points where you forgot to enter neighbors', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
        
    # Second, points with >3 neighbors
    print("Check for points with >3 neighbors")
    alertData = []
    for (point, neighbors) in checkNeighborsPerPoint(dataLines):
        if neighbors > 3:
            point = point.strip().split('\t')
            point = kenyaFixLine(point)
            point = '\t'.join(point)
            alertData.append(point)
    commentLine = writeAlert('Points with more than 3 neighbors', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for non-unique neighbors in juvenile samples
    print("Check for non-unique neighbors in juvenile samples")
    alertData = [line for line in checkUniqueNeighbors(dataLines, [stypeJuv]) if len(line) > 0 and isType(line, pntAbbrev)]
    alertData = [kenyaFixLine(line) for line in alertData]
    alertData = ['\t'.join(line) for line in alertData]
    commentLine = writeAlert('Juvenile points where you used adult female protocol for neighbors', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)
    
    # Check for data where actor is actee
    print("Check for data where actor is actee")
    selfToSelf = checkActorIsActee(dataLines)
    alertData = [kenyaFixLine(line) for line in selfToSelf if isType(line, adlibAbbrev)]
    alertData = ['\t'.join(line) for line in alertData]
    commentLine = writeAlert('Adlibs where individual interacted with itself', alertData, showSpecifics) + '\n'
    alertLines.append(commentLine)

    # No need to check for this. Amboprim8 forbids it.
    #print("Check for rows where focal is neighbor")
    #alertData = [kenyaFixLine(line) for line in selfToSelf if isType(line, neighborAbbrev)]
    #alertData = ['\t'.join(line) for line in alertData]
    #commentLine = writeAlert('Neighbor rows where focal is its own neighbor', alertData, showSpecifics) + '\n'
    #alertLines.append(commentLine)
        
    # Check for focals done that aren't in the log (if provided).
    # Exclude focals with no points.
    if focalLogPath != "":
        # Then a log was provided. Do this check.
        print("Check for focals done that aren't in the log")
        alertData = getFocalsNotLogged(dataLines, focalLogPath)
        # This level of detail is not wanted, apparently
        # alertData = [line[0]+"\t"+line[2]+" point(s) in sight, out of "+line[1] for line in alertData if int(line[1]) > 0]
        alertData = [(line[0]).strip().split('\t') for line in alertData]
        alertData = [kenyaFixLine(line) for line in alertData]
        alertData = ['\t'.join(line) for line in alertData]
        commentLine = writeAlert("Focal samples that you didn't enter in the log", alertData, showSpecifics) + '\n'
        alertLines.append(commentLine)
    
    # Check for logged (as complete) focals that aren't in the data
    if focalLogPath != "":
        # Then a log was provided. Do this check.
        print("Check for logged (as complete) focals that aren't in the data")
        alertData = []
        for line in getLoggedNotDone(dataLines, focalLogPath):
            line = line.strip().split('\t')
            alertData.append(kenyaDateTime(line[0], False) + '\t' + line[3])
        commentLine = writeAlert("Focal samples in the log but aren't in the data", alertData, showSpecifics) + '\n'
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
    print("Creating export file:", path.basename(outFilePath) )
    outFile = open(outFilePath,'w')
    
    outMsg = writeHeader(inFilePath) 
    outFile.write(outMsg + '\n\n')
    
    print("Opening import file:", path.basename(inFilePath))
    impFile = open(inFilePath, 'r')
    impFile.readline() ## Skip the header line
    allEvents = impFile.readlines()
    impFile.close()
    
    allEvents =  [line.strip().split('\t') for line in allEvents]
    
    print("Getting data summary")
    outMsg = observerDataSummary(allEvents)
    outFile.write(outMsg + '\n\n')
    
    print("Getting errors and alerts summary")
    outMsg = feedbackAlerts(allEvents, focalLogPath, showSpecifics=True)
    outFile.write(outMsg + '\n')

    print("Closing export file")
    outFile.close()
    outMsg = "Finished checking data in " + path.basename(inFilePath)
    print(outMsg)
