'''
Created on 1 Sep 2015

Code used to compile agonisms from multiple files into a single list.

Ideally, run this code with a GUI.

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''

from constants import agonismCodes

def getAgonismsFromFile(filePath, minDate, maxDate, behaviorCodes = agonismCodes):
    '''
    filePath is a string that gives the location of a txt file in the format returned by file_import.py
    minDate is the minimum allowed interaction date, maxDate is the maximum allowed interaction date. Both are strings.
        (So with minDate and maxDate of '2015-01-01' and '2015-01-31', only agonisms recorded in January 2015 will be returned)
    behaviorCodes is a list of strings, designating what act(s) indicate that a behavior is an agonism
    
    Returns a list of strings, where each string is one line representing one interaction.
    '''
    openedFile = open(filePath,'r')
    openedFile.readline() # Skip past the header line
    fileLines = openedFile.readlines()
    openedFile.close()
    agonisms = []
    for line in fileLines: # This could easily be a list comprehension, but this seems more readable
        splitLine = line.split('\t')
        if splitLine[0] == 'ADL' and splitLine[5] in agonismCodes and splitLine[2]>=minDate and splitLine[2]<=maxDate:
            agonisms.append(line)
    return agonisms

def gatherAgonisms(fileSoFarPath, newDataFilePath, minDate, maxDate):
    '''
    Does the following:
    1) pull all the agonisms from a pre-existing file (at fileSoFarPath) that lists the agonisms compiled so far
    2) add all the agonisms pulled from (1) to a set 
            (Uniqueness in the set is based on the assumption that no two agonisms were recorded in the same second)
    3) pull all the agonisms from the file at newDataFilePath, a txt file in the format returned by file_import.py
    4) add the agonisms from (3) to the same set as in (2)
    5) convert the set of unique agonisms to a list, sort it by...actor(?) and write (not append) it to the file from (1)      
    '''
    agonismsSoFar = set(getAgonismsFromFile(fileSoFarPath, minDate, maxDate))
    newAgonisms = set(getAgonismsFromFile(newDataFilePath, minDate, maxDate))
    print 'Agonisms collected so far:', len(agonismsSoFar)
    print 'Agonisms in the new file:', len(newAgonisms)
    uniqueAgonisms = agonismsSoFar | newAgonisms
    print 'New total agonisms:', len(uniqueAgonisms)
    
    # Check to see if anything was added at all
    if len(uniqueAgonisms) -  len(agonismsSoFar) <= 0: # I'm pretty sure it'll never be less than 0, but what the hey
        print 'No new agonisms added!'
    
    uniqueList = list(uniqueAgonisms)
    # Sort list by actor, actee, date, time
    uniqueList.sort(key=lambda behavior: ( behavior.split('\t')[4], behavior.split('\t')[6], behavior.split('\t')[2], behavior.split('\t')[3] ))
    
    outFile = open(fileSoFarPath, 'w')
    outFile.write('Agonisms recorded between ' + minDate + ' and ' + maxDate + '\n')
    outFile.writelines(uniqueList)
    print "Finished compiling agonisms from ", newDataFilePath



##workingFilePath = './../working_ags.txt'
##moreDataFilePath = './../output_test.txt'

##gatherAgonisms(workingFilePath, moreDataFilePath, '2015-08-05', '2050-01-01')