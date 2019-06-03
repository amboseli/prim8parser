'''
Created 23-24 May 2019

Functions for importing and comparing a) actual focal data and b) a file
showing the observer's log of who they were _supposed_ to sample. These
two are in different formats, so the import functions are useful because
they return the data in a standardized format that allows for easier
comparison.

Comparisons are intended to be coarse, useful for auto-generating
feedback for observers.  For a "fine-toothed-comb" comparison, use your
favorite data comparer (diff, BBEdit, wwwdiff, etc.).

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''

from babaseWriteHelpers import isType
from constants import *
from datetime import date, datetime
from errorCheckingHelpers import *
from operator import itemgetter


def importDataForCompares(dataLines):
    '''
    dataLines is a list of lists of strings: the data from a processed 
    prim8 data file, stripped and split.
    
    Collects all "header" rows (beginning rows for a focal sample)
    into a list.  A tab-delimited "Y" or "N" is added to each of
    these, indicating if the focal was completed.
    
        "N" is for samples that had no data, no points, or only out-
            of-sight points.
        "Y" is used for all others.
    
    After adding Y/N to each sample's header, some values in these
    rows are removed, while others are rearranged, as follows:
    
    Before:
    HDR	OBS	yyyy-mm-dd	HH:MM:SS	GGG	NNN	TTT	hh:mm:ss	Y/N
    
        HDR is the code used to indicate that this is a header.
        OBS is the observer's initials.
        yyyy-mm-dd is obvious.
        HH:MM:SS is the start time
        GGG is the group's abbreviation
        NNN is the focal individual's sname
        TTT is the focal sample type
        hh:mm:ss is the end time
        Y/N is the one-character code added, described above
    
    After:
    HH:MM:SS	yyyy-mm-dd	GGG	OBS	NNN	Y/N	FULLTEXT	NumPoints	NumIS
    
        (Same abbreviations as above, except...)
        FULLTEXT is the full text of the line in "before", joined
            together as a single string. Useful for output.
        NumPoints is an integer, indicating how many points were
            recorded in this sample. Points that occurred during this
            time but with a different focal individual are NOT
            included in this count.
        NumIS is an integer, the number of points in this sample that
            were recorded "in sight" (i.e. not out of sight). Points
            that occurred during this time but with a different focal
            individual are NOT included in this count.
        
        This order is used because it's similar to that used in the
        log file.  It makes comparisons easier to write.
    
    Returns a list of lists of strings, each list of strings for each
    focal sample, and in the "After" format shown above.
    '''
    # List of all the header rows, i.e. the focal samples
    theFocals = [line[:] for line in dataLines if isType(line, focalAbbrev)]
    
    # List of all the focals that were not "completed". This means any
    # samples with no points, or only out-of-sight points.  If we
    # first remove all the out-of-sight points, then gathering samples
    # with no points will include all of these at once.
    badData = dataLines[:]
    badData = [line[:] for line in badData if line not in pointsOutOfSight(dataLines)]
    
    # Make list of rows with no points (or only OOS points)
    incompletes = [line[:] for line in theseWithoutThose(badData, focalAbbrev, [pntAbbrev])]
    
    # Add a "Y" or "N" to each row in theFocals to indicate how
    # "complete" the sample was
    for line in theFocals:
        if line in incompletes:
            line.append("N")
        else:
        	line.append("Y")
    
    # Get points per focal
    pointsPerFocal = countPointsPerFocal(dataLines)
    # Get in-sight points per focal
    pointsISPerFocal = countPointsPerFocal(dataLines, incOutOfSights = False)
    # Convert these data to dictionaries, to simplify the next step
    pointsPerFocal = {focal:points for (focal, points) in pointsPerFocal}
    pointsISPerFocal = {focal:points for (focal, points) in pointsISPerFocal}
    
    # Now rearrange the columns into their desired output format
    outData = []
    for line in theFocals:
        newLine = []
        newLine.append(line[3]) # Time
        newLine.append(line[2]) # Date
        newLine.append(line[4]) # Grp
        newLine.append(line[1]) # Observer
        newLine.append(line[5]) # Sname
        newLine.append(line[-1]) # Complete
        fullText = "\t".join(line[:-1]) # Omit the "complete" value
        newLine.append(fullText) # Fulltext
        numPoints = pointsPerFocal[fullText]
        newLine.append(str(numPoints)) # NumPoints
        numIS = pointsISPerFocal[fullText]
        newLine.append(str(numIS)) # NumIS
        outData.append(newLine)
    
    return outData


def importLogFile(logFilePath):
    '''
    logFilePath is a string containing the path to a focal sample log
    file. (This file is transcribed in the US from the observers' 
    handwritten logs.)  The format for this file is expected to be as
    follows:
        (tab-delimited)
        num	date	grp	observer	sname	completed
        1	dd/mm/yyyy	GGG	OBS	NNN	Y
        ...
        
        "num": a number, probably sequential, used to retain the order
            in which these samples occurred.
        "date": obvious. Must be in format dd/mm/yyyy.
        "grp": obvious. Must be 3 letters, all caps.
        "observer": obvious.  Should be all caps.
        "sname": obvious. 3 letters, all caps.
        "completed": "Y" if the observer noted that the focal was
            completed, "N" if the observer noted it wasn't, or if the
            observer didn't note this at all.
    
    The date in this file is a different format from what's usually
    used in these prim8 files.  It is the usual format used by the
    baboon project's data entry in the US: dd/mm/yyyy.  To standardize
    for comparison, this date is converted to yyyy/mm/dd "behind the
    scenes" in this function, but the data in the file are never
    replaced with the new format.
    
    The file is opened, the header is discarded, and the rest of the
    data are stripped, split, and gathered into a list of lists of
    strings. After the date format is changed as described above, the
    data are sorted by observer, date, grp, then num.
    
    This function takes the file path, and not the data from the file,
    because these "log" data are pretty niche and unusual.  Lots of
    functions and packages use the "dataLines" from a processed prim8
    file, but we don't expect to see any other functions that will
    work with the log data.  It doesn't seem necessary to split up the
    importing of the log file and the processing of its data.
    
    Returns a list of lists of strings: the rows from the log file
    with reformatted dates and sorted.
    '''
    logFile = open(logFilePath, "rU")
    logFile.readline() # Skip header
    logData = logFile.readlines()
    logFile.close()
    
    logData = [line.strip().split() for line in logData]
    
    # Convert dates to preferred format, and convert the "num" column
    # from string to integer
    for line in logData:
        oldDate = datetime.strptime(line[1], '%d/%m/%Y')
        line[1] = date.strftime(oldDate, '%Y-%m-%d')
        line[0] = int(line[0])
    
    # Sort data by observer, date, grp, num
    logData.sort(key = itemgetter(3, 1, 2, 0))
    
    return logData


def getFocalsNotLogged(dataLines, logFilePath):
    '''
    For each _actual_ focal sample in dataLines, checks to see if it
    was logged.
    
    dataLines is a list of lists of strings: the data from a processed 
    prim8 data file, stripped and split.  logFilePath is a string
    containing the path to a focal sample log file.
    
    Returns a list of (full header text, number of points, number of
    points in sight) tuples, those samples that happened but which
    were not logged.
 
    "Completeness" is mostly ignored in this check, except as 
    discussed below.  It's not a value that is recorded by observers
    in the field, so it doesn't seem very relevant to _this_
    comparison.
    
    Output includes a count of how many points were recorded in the
    sample.  This is intended to be a signal to help discriminate
    between duplicate samples that occurred 1) because one of them
    ended too early, and 2) full samples that were just not logged,
    for whatever reason.
    
    When a focal sample is found in the list of logged samples, the
    sample is removed from the list of logged samples. (If more than
    one row in the log matches, the _first_ matching row is removed.)
    This helps ensure that if an individual is incorrectly sampled
    multiple times in a day, this doesn't get hidden by a single
    legitimate sample.  In hopes of focusing output on "problematic"
    rows, all the samples that are indicated as "complete" (with a 
    "Y") are compared first.  So if there are two samples for one 
    individual on one day (one complete, one not), and the log has
    only one sample for that individual, the not-complete sample will
    always be returned and not the complete one, no matter which
    happened first.
   '''
    realFocals = importDataForCompares(dataLines)
    logFocals = importLogFile(logFilePath)
    
    # Sort realFocals so that the complete ones are on top
    realFocals.sort(key = itemgetter(5), reverse = True)
    
    # Convert logFocals to list of strings and only keep the values
    # that we'll use in this comparison (Date, Grp, Observer, Sname)
    logFocals = ['\t'.join(line[1:5]) for line in logFocals]
    
    # Create the list that we'll eventually return
    notLogged = []
    
    for line in realFocals:
        thisFocal = '\t'.join(line[1:5]) #Date, Grp, Observer, Sname
        try: # Find thisFocal in logFocals
            logIdx = logFocals.index(thisFocal)
            # Hooray, we found it. Remove this focal from the log
            #print "Found the focal, now remove it from the log"
            logFocals.pop(logIdx)
        except ValueError:
            # Focal not found in log. This needs to be returned.
            #print "Focal not logged:", thisFocal, ",", line[-2], "point(s)", line[-1], "point(s) in sight"
            notLogged.append(line)
    
    # Before returning the list of not-logged samples, sort them by
    # observer, date, time. Then prune away extra/redundant data.
    notLogged.sort(key = itemgetter(3, 1, 0))
    notLogged = [(line[-3], line[-2], line[-1]) for line in notLogged]
    
    return notLogged


def getLoggedNotDone(dataLines, logFilePath):
    '''
    For each logged sample, checks to see if a real sample actually
    happened.
    
    dataLines is a list of lists of strings: the data from a processed 
    prim8 data file, stripped and split.  logFilePath is a string
    containing the path to a focal sample log file.
    
    Returns a list of strings.  Each one is a row from the log file
    for a sample that was logged as complete but which is not in the
    data.
    
    Samples logged as not complete may be in the data, or might not be
    there at all. Because of this, this function ignores samples that
    were logged incomplete.
    
    Admittedly, the way this function works is VERY similar to the
    previous function.  Arguably, a more universal function could be
    written and just invoked twice.
    '''
    realFocals = importDataForCompares(dataLines)
    logFocals = importLogFile(logFilePath)
    
    # Remove logged focals that aren't complete
    logFocals = [line for line in logFocals if line[5] =='Y']
    
    # Convert realFocals to a list of strings, useful for comparison
    realFocals = ['\t'.join(line[1:5]) for line in realFocals]
    
    # Create the list that we'll eventually return
    notDone = []
    
    for line in logFocals:
        thisFocal = '\t'.join(line[1:5]) # Date, Grp, Observer, Sname
        try: # Find thisFocal in realFocals
            realIdx = realFocals.index(thisFocal)
            # Found the logged focal in the real data. Now remove it
            # from the log
            realFocals.pop(realIdx)
        except ValueError:
            # Logged focal not in data. Add it to the list of data
            # that will be returned
            #print "Logged focal not found in actual data:", thisFocal
            notDone.append(thisFocal)
    
    return notDone
