'''
Created on 21 May 2019

Code used to intelligently combine the data from multiple files into a
single list/file, within a specified date range.

This is different from the "gatherAgonisms" package in that it doesn't
restrict which kind(s) of data it gathers, and that it intelligently
retains the order of lines entered with the same date and time (mostly
important for neighbor lines, but occasionally Prim8 wigs out and
somehow multiple other lines are recorded at the same time, as well.)

Ideally, run this code with a GUI.

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''

def getDataFromFile(filePath, minDate, maxDate):
    '''
    filePath is a string that gives the location of a txt file in the
	format returned by readDumpFile.py.

    minDate is the minimum allowed interaction date, maxDate is the
	maximum allowed interaction date. Both are strings.
	
        (So with minDate and maxDate of '2015-01-01' and '2015-01-31',
        only data recorded in January 2015 will be returned)
    
    Except for the first row, all rows are presumed to be strings with
    tab-delimited data, with a date in position [2] and time in
    position [3].
    
    Returns a list of strings, where each string is one line from the
	source file.  Except for the header, all lines have a tab-
	delimited numeral added to the end of the row. For most lines,
	this row will be 0 (zero), but when more than one row occurs with
	the same date and time, this value will increase in successive
	rows. For example, the first line is 0, the next is 1, the next is
	2, etc.  These numerals are intended to be useful for sorting
	purposes later, and are intended to be removed before the data are
	written to a new file.
    '''
    outLines = []
    openedFile = open(filePath,'rU')
    # Add the file's header to the outward list
    outLines.append(openedFile.readline())
    fileLines = openedFile.readlines()
    openedFile.close()
    
    # Make some constants to work with while iterating
    lastDateTime = ''
    thisRowNum = 0
    
    for line in fileLines:
        splitLine = line.split('\t')
        if splitLine[2] >= minDate and splitLine[2] <= maxDate:
            # Then this line is within the desired date range. Keep
            # going.
            thisRowDateTime = splitLine[2] + " " + splitLine[3]
            if thisRowDateTime <> lastDateTime:
                # This row is at a new, not-yet-seen date/time. Reset
                # the constants.
                lastDateTime = thisRowDateTime[:]
                thisRowNum = 0
            # Add number to the end of the line, for sorting later
            newLine = line + '\t' + str(thisRowNum)
            outLines.append(newLine)
            thisRowNum += 1
    return outLines


def gatherData(fileSoFarPath, newDataFilePath, minDate, maxDate):
    '''
    Does the following:
    1) pull all the data from a pre-existing file (at fileSoFarPath) that
	contains the data compiled so far
    2) add all the data pulled from (1) to a set
    3) pull all the data from the file at newDataFilePath, a txt file in
	the format returned by readDumpFile.py
    4) add the data from (3) to the same set as in (2)
    5) convert the set of unique data to a list, sort it, and write--not
	append--it to the file from (1)
	
	Except for the file's header, all rows are presumed to have a tab-
	delimited number added to the end of the string, for sorting 
	purposes.  These extra numerals are removed before writing data in
	(5).
	
	When gathering data, the file header can be retained.  If the
	pre-existing file in (1) is empty, then the header of the "new"
	file (3) will be retained.  If not empty, the first line of both
	(1) and (3) are compared.  If identical, then that header is used
	in the final output file (5).  If not identical, then a new
	header is used in (5) indicating that multiple file headers were
	used.
    '''
    from constants import multiFileHeader
    from os import path
    
    # Open/import previously-compiled data.
    dataSoFar = getDataFromFile(fileSoFarPath, minDate, maxDate)
    dataSoFarIsEmpty = False
    
    # Check the header in the previously-compiled data file.
    dataSoFarHeader = ''
    if len(dataSoFar) > 1:
        dataSoFarHeader = dataSoFar.pop(0)
    elif dataSoFar[0] == '':
        # dataSoFar is empty. So there's no old header to deal
        # with.
        dataSoFarIsEmpty = True
        # Get rid of this one empty row
        dataSoFar.pop()
    
    # Open/import new data.
    newData = getDataFromFile(newDataFilePath, minDate, maxDate)
    
    # Check the header in the new data.
    newDataHeader = ''
    if len(newData) > 1:
        newDataHeader = newData.pop(0)
    elif newData[0] == '':
        # New file is empty, no work to be done
        print "New data file is empty, no work to do"
        return "New data file is empty, no work to do"
    
    # Merge the two headers as needed
    if newDataHeader <> dataSoFarHeader and not dataSoFarIsEmpty:
        # The files have different non-NULL headers, so use the
        # designated header made to indicate this
        newDataHeader = multiFileHeader[:]
    # Else they are equal, or the "so far" file is empty. Either way,
    # use the newDataHeader
    
    # Convert these data to sets
    dataSoFar = set(dataSoFar)
    newData = set(newData)
    
    # Tell the user what's happening
    print 'Lines of data already collected:', len(dataSoFar)
    print 'Lines of data in the new file:', len(newData)
    uniqueData = dataSoFar | newData
    print 'New total # of lines:', len(uniqueData)
    
    # Check to see if anything was added at all
    if len(uniqueData) -  len(dataSoFar) == 0:
       print 'No new data added!'
    
    # Convert the set to a list, so we can put them in order
    uniqueList = list(uniqueData)
    # Sort list by date, then time, then the last tab-delimited field
    # (the added number for sorting).
    uniqueList.sort(key=lambda behavior: ( behavior.split('\t')[2], behavior.split('\t')[3], behavior.split('\t')[-1] ))
    
    # Now that they're sorted, remove the tab-delimited numeral added
    # at the end of each row.
    uniqueList = [line[:(line.rfind('\t'))] for line in uniqueList]
    
    # Write to the new file. Header first, then the rest of the data.
    outFile = open(fileSoFarPath, 'w')
    outFile.write(newDataHeader)
    outFile.writelines(uniqueList)
    outFile.close()
    
    print "Finished compiling data from ", path.basename(newDataFilePath), "to", path.basename(fileSoFarPath)

