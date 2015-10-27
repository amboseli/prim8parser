'''
Created on 15 Sep 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

Functions involved with reading processed Prim8 data and writing SQL to add the data to Babase.

'''

from babaseWriteHelpers import *

def writeAll(dataFilePath, sqlFilePath, commitTransaction = False):
    '''
    dataFilePath and sqlFilePath are both strings.
    commitTransaction is a boolean that indicates whether the output SQL should be committed.  
    
    1) Reads the data from the file at dataFilePath (should be a .txt file processed from a Prim8 data file)
    2) Generates SQL to add the data to Babase
    3) Writes the SQL to the file at sqlFilePath
    
    Eventually, we'll probably change this function to send SQL to stdout, or at least provide the option to do it that way.
    
    Doesn't return anything.
    '''
    from constants import focalAbbrev, neighborAbbrev, noteAbbrev, adlibAbbrev, pntAbbrev, outOfSightValue
    from babaseWriteHelpers import behavDuringFocal
    
    dataFile = file(dataFilePath, 'ru')
    
    # Important values used throughout the for loop     
    prgID, setupID, tabletID = getProgramSetup(dataFile.readline()) # Read first line from file 
    dataLines = [line.strip().split('\t') for line in dataFile.readlines()] # Note that the header from the file has already been read, so it's omitted here.
    dataFile.close()
    sampleMins = countMins(dataLines)
    lastFocal = []
    pntNum = 0 #Keep track of the current "min" value for points
    sqlOut = []
    
    thisWholeFocal = [] #List of lists of strings
    lastPoint = [] # List of lists of strings
    nghNum = 0
    mistakeOut = [] #List of lists of strings
    allHdrs = 0
    allPnts = 0
    allNghs = 0
    allTxts = 0
    allAdls = 0
    adlMECs = 0
    adlMEC_notfocal = 0
    pntsWONghs = 0
    nghsWOPnts = 0
    tooManyPnts = 0
    orphanTxts = 0
    
    # Write SQL
    sqlOut.append('BEGIN;\n') #Add text to start an SQL transaction
    
    for line in dataLines:
        if line[0] == focalAbbrev:
            if pntNum > 10:
                tooManyPnts += 1
                errText = ['''\nToo many points ({0} found):'''.format(pntNum)]
                mistakeOut.append(errText)
                for item in thisWholeFocal:
                    mistakeOut.append(item)
            if  nghNum != 3 and len(lastPoint) > 0:
                if lastPoint[0][6] == outOfSightValue:
                    errText = 'Do nothing'
                elif nghNum > 3:
                    nghsWOPnts += 1
                    errText = ['''\nToo many neighbors ({0} found):'''.format(nghNum)]
                    mistakeOut.append(errText)
                    for item in lastPoint:
                        mistakeOut.append(item)
                elif nghNum < 3:
                    pntsWONghs += 1
                    errText = ['''\nToo few neighbors ({0} found):'''.format(nghNum)]
                    mistakeOut.append(errText)
                    for item in lastPoint:
                        mistakeOut.append(item)
            lastFocal = line[:]
            pntNum = 0
            lineString = '\t'.join(line)
            allMins = sampleMins[lineString]
            outLine = newFocal(line, allMins, prgID, setupID, tabletID)
            sqlOut.append(outLine)
            thisWholeFocal = []
            thisWholeFocal.append(line)
            lastPoint = []
            nghNum = 0
            allHdrs += 1

        elif line[0] == pntAbbrev:
            if len(lastPoint) > 0 and lastPoint[0][6] != outOfSightValue:
                if pntNum > 0:
                    if  nghNum != 3:
                        if nghNum > 3:
                            nghsWOPnts += 1
                            errText = ['''\nToo many neighbors ({0} found):'''.format(nghNum)]
                            mistakeOut.append(errText)
                            for item in lastPoint:
                                mistakeOut.append(item)
                        elif nghNum < 3:
                            pntsWONghs += 1
                            errText = ['''\nToo few neighbors ({0} found):'''.format(nghNum)]
                            mistakeOut.append(errText)
                            for item in lastPoint:
                                mistakeOut.append(item)
            pntNum += 1
            allPnts += 1
            nghNum = 0
            thisWholeFocal.append(line)
            lastPoint = []
            lastPoint.append(line)
            
            if line[6] == outOfSightValue: # Then we don't want the point recorded at all
                continue
            outLine = newPoint(line, pntNum)
            sqlOut.append(outLine)

        elif line[0] == neighborAbbrev:
            if len(lastPoint) == 0: # Neighbors added at beginning of focal without a PNT line first
                nghsWOPnts += 1
                errText = ['''\nNeighbor line without a preceding PNT:''']
                mistakeOut.append(errText)
                mistakeOut.append(line)
                lastPoint.append(line)
            elif lastPoint[0][0] != pntAbbrev: # More neighbor lines without a PNT first
                nghsWOPnts += 1
                mistakeOut.append(line)
                lastPoint.append(line)
            nghNum += 1
            allNghs += 1
            thisWholeFocal.append(line)
            lastPoint.append(line)
                        
            if neighborIsNull(line): # Then we don't want this false neighbor recorded
                continue
            outLine = newNeighbor(line, lastFocal)
            sqlOut.append(outLine)
            
        elif line[0] == adlibAbbrev:
            allAdls += 1
            if line[6] in ['M','E','C']:
                adlMECs += 1
                if behavDuringFocal(lastFocal, line):
                    currFocal = lastFocal[5]
                    actor, actee = (line[5],line[7])
                    if currFocal not in [actor, actee]:
                        adlMEC_notfocal += 1
                        errText = ['''\nM/E/C found outside of a focal:''']
                        mistakeOut.append(errText)
                        mistakeOut.append(line)
                else:
                    adlMEC_notfocal += 1
                    errText = ['''\nM/E/C found outside of a focal:''']
                    mistakeOut.append(errText)
                    mistakeOut.append(line)
            if behavDuringFocal(lastFocal, line):
                thisWholeFocal.append(line)
            outLine = newInteraction(line, lastFocal)
            sqlOut.append(outLine)
            
        elif line[0] == noteAbbrev:
            # TODO: Waiting for clarification from leaders about handling these data. What if they're outside a focal? Before any focals for the day? Long after a focal ended?
                # Written this way, notes before any focals in a file will be associated with whichever sample was last uploaded before this file. 
            allTxts += 1
            if not behavDuringFocal(lastFocal, line):
                orphanTxts += 1
                errText = ['''\nNote found outside of a focal:''']
                mistakeOut.append(errText)
                mistakeOut.append(line)
                continue
                
            thisWholeFocal.append(line)    
            outLine = newNote(line)
            sqlOut.append(outLine)
    
    # Correct instances of 'NULL' to just say NULL 
    #sqlOut = [line.replace("'NULL'", "NULL") for line in sqlOut]
        
    # Wrap it all up
    transactionEnd = transactionCommit(commitTransaction) + "\n"
    sqlOut.append(transactionEnd)
    
    # Open file, write data
#    sqlFile = file(sqlFilePath, 'w')
#    sqlFile.writelines(sqlOut)
#    sqlFile.close()
    
    # Open and append "mistake" file
    hdrOut = '''{0} focals found. {1} of them had >10 points ({2}%). (Search for "Too many points")\n'''.format(allHdrs, tooManyPnts, 100 * float(tooManyPnts)/float(allHdrs))
    pntOut = '''{0} PNT lines found. {1} of them were in-sight but had no neighbors ({2}%). (Search for "Too few neighbors")\n'''.format(allPnts, pntsWONghs, 100 * float(pntsWONghs)/float(allPnts))
    nghOut = '''{0} NGH lines found. {1} of them had no associated PNT row ({2}%). (Search for "Too many neighbors" or "Neighbor line without")\n'''.format(allNghs, nghsWOPnts, 100 * float(nghsWOPnts)/float(allNghs))
    adlOut = '''{0} ADL lines found. {1} of them are M/E/C, and {2} of those did not involve the focal ({3}%). (Search for "M/E/C")\n'''.format(allAdls, adlMECs, adlMEC_notfocal, 100 * float(adlMEC_notfocal)/float(adlMECs))
    txtOut = '''{0} TXT lines found. {1} of them were outside of a focal sample ({2}%). (Search for "Note found")\n'''.format(allTxts, orphanTxts, 100 * float(orphanTxts)/float(allTxts))
    
    mistakeFile = file('/Users/jg177/Desktop/Sep2015.txt', 'wu')
    mistakeFile.write(hdrOut)
    mistakeFile.write(pntOut)
    mistakeFile.write(nghOut)
    mistakeFile.write(adlOut)
    mistakeFile.write(txtOut)
    mistakeFile.write('\n')
    
    for item in mistakeOut:
        lineString = '\t'.join(item)+'\n'
        mistakeFile.write(lineString)
    
    mistakeFile.close()

if __name__ == '__main__':
    testInPath = "/Users/jg177/Desktop/Team's Data/SAMSUNG FOCAL DATA/Sept 2015 ALL DATA.txt"
    testOutPath = './../testSQL.txt'
    writeAll(testInPath, testOutPath, False)