'''
Created on 28 Oct 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''
from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from errorCheckingHelpers import *
from datetime import datetime
from os import path

def errorCheck (inFilePath, outFilePath):
    '''
    Checks the data in the file at inFilePath for possible errors.
    Also does some counting of basic statistics about the data, e.g. (how many focals, how many adlibs, etc.)
    Errors, alerts, and statistics will be written to the file at outFilePath. 
    Prints a message that the process is complete.
    Returns nothing.
    
    Consider breaking this up into some smaller functions?  Maybe run the counts
    and by-line analyses for each date instead of just once for everything?
    Another day.
    '''
    from constants import focalAbbrev, pntAbbrev, neighborAbbrev, adlibAbbrev, noteAbbrev, emptyAbbrev, outOfSightValue
    
    print "Creating export file:", path.basename(outFilePath) 
    outFile = open(outFilePath,'w')
    
    outMsg = writeHeader(inFilePath) 
    outFile.write(outMsg + '\n\n')
    
    print "Opening import file:", path.basename(inFilePath)
    impFile = open(inFilePath, 'r')
    impEvents = impFile.readlines()
       
    print "Adding all lines to allEvents list"
    allEvents =  [line.strip().split('\t') for line in impEvents] ##List of all lines read from the import file (impFile)
    allEvents.pop(0) ##Remove the "Parsed data..." line at the top
    
    print "Getting data summary"
    outMsg = dataSummary(allEvents)
    outFile.write(outMsg + '\n\n')
    
    print "Getting errors and alerts summary"
    outMsg = errorAlertSummary(allEvents)
    outFile.write(outMsg + '\n')

    print "Closing export file"
    outFile.close()
    outMsg = "Finished checking data in " + path.basename(inFilePath)
    print outMsg

if __name__ == '__main__':
    
    #impPath = askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='Select a processed prim8 file:')
    impPath = './../output_test.txt'

    #outPath = asksaveasfilename(defaultextension='.txt', title='Name for the error summary file?')
    outPath = './../file_summary.txt'
    
    errorCheck(impPath, outPath)
