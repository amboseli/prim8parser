print "Opening import file"
impFile = open("./../import_test.csv", 'r')

print "Creating export file"
outFile = open('./../output_test.txt','w')

def removeExtraNewLines(file):
    '''
    Given an opened file, reads through the data and removes all newline characters (but not carriage returns), then adds a newline after each carriage return.
    Next, splits the text into a list of strings, separated by newlines.
    Closes the opened file.
    Returns a list of strings: one string per line from file, with carriage returns/newlines removed.
    
    Useful because the team's data occasionally includes newline characters (but not carriage returns) in the middle of their data, e.g. "Out of S\night"  
    It's not yet clear how this is happening, but these unwanted newlines cause trouble when reading the data file one line at a time.  
    '''
    print "Reading raw input file"
    fullText = file.read()
    fullText = fullText.replace(u"\u000A","") ##Replace all newlines ('\n') with nothing
    fullText = fullText.replace(u"\u000D",u"\u000D\u000A") ##Replace all carriage returns ('\r') with carriage return, new line ('\r\n')
    print "Finished checking for unwanted newlines"
    file.close()
    return fullText.splitlines()

def makeAllDicts(openedFile):
    '''
    Given an opened file, reads processes the data into a dictionary of dictionaries.  Each of the "inner" dictionaries is essentially one "table" of data from the input file.
    Closes the opened file.
    The names of each of the "inner" dictionaries is given by the local list, "tableList".
    Returns the dictionary of dictionaries.
    '''
    allLines = removeExtraNewLines(openedFile) ##Get data. Closes file.
    allLines = [line.split(",") for line in allLines] ##Split lines. The source file is CSV
    
    fullDict = {} ##The big, bad dictionary of dictionaries returned by this function
    
    ##These NEED to be spelled the same way as they are in the data file.  Case sensitive.  Order in this list is not important, however.
    tableList = ['adlib', 'sites', 'observers', 'groups','species','individuals', 'biologicalsamples','coordinatesystem','locations','workcalendars','behaviortypes','behaviors','focalfollows','scans','behaviorinstances','focalbehaviors','scanbehaviors','modifiers'] 
    
    for table in tableList: ##Create a bunch of empty dictionaries, with names from tableList
        fullDict[table] = {}
    
    currentDict = '' ##Used in the below "for" loop, to indicate which dictionary to add all the data
    for n,line in enumerate(allLines): ##Enumerating and adding n to allow the return of line numbers in case there's an error
        if len(line) == 1: ##Then the line should indicate the beginning of a new table.  Until a new table starts, all following lines should be added to the dictionary of this name.
            if line[0] not in tableList: ##Then there's a problem in the file
                print "Problem at line", (n+1), ":", line[0], " is not a recognized table name"
                fullDict = {} ##Empty the dictionary, to essentially halt any processes that may come after
                return fullDict 
            print 'Finished with', currentDict, 'dictionary. Begin', line[0], 'dictionary.'
            currentDict = line[0]
        else: ##Line should be actual data to add to a table
            for x,item in enumerate(line): ##Check for numbers that are saved as strings
                if item.isdigit(): ##then item is a number and shouldn't stay a string
                    line[x] = int(item)
            fullDict[currentDict][line[0]] = line[1:] ##Set the first column of the data as the key, everything else as the value
            print 'Added', line[1:], "to", currentDict, 'with key #', line[0]
    print 'Finished creating dictionary of dictionaries!'
    return fullDict

makeAllDicts(impFile)

outFile.close()
            
