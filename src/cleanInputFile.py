'''
Created on 27 Aug 2015

@author: jg177

    Functions used to clean and process data from the prim8 import file into data usable by the rest of the program.

'''

import csv

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

def cleanInputData(openedFile):
    '''
    Given an opened file, processes its data into a list of lists of strings, ready to be parsed.
    Closes the opened file.
    Performs comma-separated split using csvreader, to account for the possibility of commas in data fields.
    Returns a list of lists of strings: each (inner) list of strings represents one line of data from openedFile. 
    '''
    fullText = removeExtraNewLines(openedFile)
    fullText = csv.reader(fullText, delimiter=',', quotechar='"')
    return fullText