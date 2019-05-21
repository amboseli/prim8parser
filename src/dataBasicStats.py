'''
Created on 31 May 2016

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

Stuff related to collecting some basic statistics about the data in a processed
prim8 data file, or a file of monthly gathered agonisms.

The original purpose of this is just to count observer agonisms/sampling day in
the monthly agonisms file.  But there's potential for so much more, so let's
leave it that way.
'''

def groupedData(dataLines, idxOfInterest):
    '''
    Reads the data in dataLines and returns it sorted in a dictionary. Each item
    in dataLines is a list (split from a string), and the "keys" in the returned
    dictionary are all the distinct values at "idxOfInterest" in all these
    lists.  The "value" in the dictionary corresponding to each key is a list of
    the lists having the "key" at their index of interest.

        For example, if the data in dataLines looks like this:
            ['AAA','BBB','AAA','BBB']
            ['AAA','XXX','YYY','ZZZ']
            [123, 456, 'AAA','BBB']
            ['AAA', 456, 'CCC', 'DDD']
        A call of groupedData(dataLines, 0) would have two keys: AAA and 123.
        The corresponding value for 'AAA' would be a list of three lists: the
        three lists beginning with 'AAA'. The list beginning with '123' does
        have 'AAA', but not at the index of interest, so this list is not part
        of the 'AAA' values.
    
    dataLines should be a list of lists, presumably strings read from a file
    that were split from tab-delimited data.
    '''
    
    myDict = {}
    
    for thisLine in dataLines:
        if thisLine[idxOfInterest] in myDict.keys():
            myDict[thisLine[idxOfInterest]].append(thisLine)
        else:
            myDict[thisLine[idxOfInterest]] = [thisLine]
    
    return myDict

if __name__ == '__main__':
    myFilePath = "/Users/jg177/Dropbox (Duke Bio_Ea)/Alberts Lab/ABRP_Data Management/DATA/REPRESENTATIVE INTERACTIONS/Final Data/AGONISM/2018/Samsung Agonisms/2018-09 Samsung Agonisms.txt"
    observerIdx = 1
    dateIdx = 2
    
    myFile = open(myFilePath, 'r')
    myFile.readline() #Skip first line, assuming it's some header
    myData = myFile.readlines()
    myFile.close()
    myData = [line.strip().split('\t') for line in myData]
    #Remove interactions with "NULL" actor or actee
    myData = [line for line in myData if line[5] <> 'NULL' and line[7] <> 'NULL']
    
    obsDict = groupedData(myData, observerIdx)
    for (obs, obsLines) in obsDict.iteritems():
        numData = len(obsLines)
        dateDict = groupedData(obsLines, dateIdx)
        numDistinctDates = len(dateDict.keys())
        print obs, "had", numData, "agonisms in", numDistinctDates, "days"
        print "\t", numData, "/", numDistinctDates, "=", (float(numData)/float(numDistinctDates)), "lines/day"
    