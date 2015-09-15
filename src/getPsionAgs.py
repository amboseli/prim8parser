'''
Created on 10 Sep 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

Unlikely that this will be used much, but I'm making it just in case.

Code to read through a Psion data file and write its agonisms to a new file.

The new file will record the agonisms in the same format exported by rawFileImportGUI.

Because this isn't intended to be used much (at all?) beyond right now, it isn't
    carefully documented.

'''

adlibCode = '<ADL>'
agonismCode = 'A'

def getPsionLines(psionFilePath):
    '''
    Give a file path for a Psion file. Opens the file, reads and splits(',') lines, closes the file.
    Returns a list of lists.
    '''
    inputFile = open(psionFilePath,'ru')
    allLines = inputFile.readlines()
    inputFile.close()
    return [line.split(',') for line in allLines]

def getPsionDate(psionLine):
    '''
    Given a list of strings which together represents a single line from a Psion file.
    Returns the date (yyyy-mm-dd) as a string.
    '''
    dateItem = psionLine[1]
    theYear = '20'+dateItem[0:2]
    theMonth = dateItem[2:4]
    theDay = dateItem[4:6]
    return '-'.join([theYear,theMonth,theDay])

def getPsionAgonisms(psionFilePath, writeToPath):
    '''
    Given a Psion file path, write its agonisms to a file at writeToPath, in the format used by rawFileImportGUI
    
    ADL    SNS    2015-09-07    07:00:11    VOG    VES    G    VEJ
    '''
    from constants import adlibAbbrev
    allLines = getPsionLines(psionFilePath)
    print 'Writing data at', writeToPath
    outFile = open(writeToPath, 'wu')
    outFile.write('Agonisms extracted from Psion data\r\n')
    
    lastObserver = ''
    lastGrp = ''
    
    for line in allLines:
        if line[0] == '<HDR>':
            lastObserver = line[7]
            lastGrp = line[6]
        elif line[0] == adlibCode and line[3] == agonismCode:
            outData = [adlibAbbrev, lastObserver, getPsionDate(line), line[2], lastGrp, line[4], line[5], line[6]]
            outLine = '\t'.join(outData)
            print outLine
            outFile.write(outLine)
    outFile.close()
    print 'Finished getting data from', psionFilePath
     

##testPath = './../testpsiondata.pts'
##testOutPath = './../testPsionFileOut.txt'

##print getPsionLines(testPath)
##getPsionAgonisms(testPath, testOutPath)