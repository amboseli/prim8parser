'''
Created on 15 Sep 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

Functions involved with reading processed Prim8 data and writing SQL to add the data to Babase.

'''

from babaseWriteHelpers import *
from babaseSQL import selectThisLine

def writeAll(dataFilePath, sqlFilePath, commitTransaction = False):
    '''
    dataFilePath and sqlFilePath are both strings.
    commitTransaction is a boolean that indicates whether the output SQL should be committed.  
    
    1) Reads the data from the file at dataFilePath (should be a .txt file processed from a Prim8 data file)
    2) Generates SQL to add the data to Babase
    3) Writes the SQL to the file at sqlFilePath
    
    Free-form text notes may be recorded before any samples in a day, in which
    case they'll be associated with the next sample to occur that day. Because
    of this, text notes are gathered and matched to a focal before the main read
    through all of the data. If a note is recorded on a day with no focals, IT
    WILL BE IGNORED.
    
    Eventually, we'll probably change this function to send SQL to stdout, or at
    least provide the option to do it that way.
    
    Doesn't return anything.
    '''
    from constants import focalAbbrev, neighborAbbrev, noteAbbrev, adlibAbbrev, pntAbbrev, outOfSightValue
    
    dataFile = open(dataFilePath, 'r')
    
    # Important values used throughout the for loop     
    prgID, setupID, tabletID = getProgramSetup(dataFile.readline()) # Read first line from file 
    dataLines = [line.strip().split('\t') for line in dataFile.readlines()] # Note that the header from the file has already been read, so it's omitted here.
    dataFile.close()
    sampleMins = countMins(dataLines)
    allNotes = collectTxtNotes(dataLines) #Get notes and match them with focals.
    lastFocal = []
    pntNum = 0 #Keep track of the current "min" value for points
    sqlOut = []
        
    # Write SQL
    sqlOut.append('BEGIN;\n') #Add text to start an SQL transaction
    
    for line in dataLines:
        if line[0] == noteAbbrev:
            continue # Because we've already dealt with all the notes

        outLine = selectThisLine(line)
        sqlOut.append(outLine)
        if line[0] == focalAbbrev:
            lastFocal = line[:]
            pntNum = 0
            lineString = '\t'.join(line)
            numMins = sampleMins[lineString]
            outLine = newFocal(line, numMins, prgID, setupID, tabletID)
            sqlOut.append(outLine)
            
            # Now write SQL for all notes associated with this sample
            #  This means that notes won't be added chronologically, but Babase doesn't care.
            sampleNotes = allNotes[lineString]
            if len(sampleNotes) > 0:
                for note in sampleNotes:
                    outLine = selectThisLine(note)
                    sqlOut.append(outLine)
                    outLine = newNote(note)
                    sqlOut.append(outLine)

        elif line[0] == pntAbbrev:
            pntNum += 1
            nghNum = 0
            if line[6] == outOfSightValue: # Then we don't want the point recorded at all
                continue
            outLine = newPoint(line, pntNum)
            sqlOut.append(outLine)

        elif line[0] == neighborAbbrev:
            nghNum += 1
            if neighborIsNull(line): # Then we don't want this false neighbor recorded
                continue
            outLine = newNeighbor(line, lastFocal)
            sqlOut.append(outLine)
            
        elif line[0] == adlibAbbrev:
            outLine = newInteraction(line, lastFocal)
            sqlOut.append(outLine)
    
    # Correct instances of 'NULL' to just say NULL 
    sqlOut = [line.replace("'NULL'", "NULL") for line in sqlOut]
    
    # Wrap it all up
    transactionEnd = transactionCommit(commitTransaction) + "\n"
    sqlOut.append(transactionEnd)
    
    # Open file, write data
    sqlFile = open(sqlFilePath, 'w')
    sqlFile.writelines(sqlOut)
    sqlFile.close()
    
#if __name__ == '__main__':
#    testInPath = "/Users/jg177/Desktop/Team's Data/SAMSUNG FOCAL DATA/Sept 2015 ALL DATA.txt"
#    testOutPath = './../testSQL.txt'
#    writeAll(testInPath, testOutPath, False)