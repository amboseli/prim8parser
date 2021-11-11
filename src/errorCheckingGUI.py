'''
Created on 16 Nov 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

A GUI for checking data files for errors and potentially-problematic events.

Adapted from the babaseWriterGUI.
'''

from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from babaseWriter import writeAll
from errorChecking import errorCheck
from os import path

class errorCheckingGUI(Frame):
    '''
    Create the GUI used for checking processed Prim8 data for issues
    '''
    
    def __init__(self, root):
        '''
        Build the GUI.
        '''
        Frame.__init__(self, root)
        
        # Define labels
        l1 = Label(root, text="Processed prim8 data file:")
        l2 = Label(root, text="Focal sample log file (optional):")
        l3 = Label(root, text="File to write summary to:")
        l3a = Label(root, text="(autofilled)")
        l4 = Label(root, text="File to write SQL to:")
        l4a = Label(root, text="(autofilled)")
        
        # Place (grid) labels
        l1.grid(row=0)
        l2.grid(row=1)
        l3.grid(row=2)
        l3a.grid(row=3, column = 1)
        l4.grid(row=4)
        l4a.grid(row=5, column = 1)
        
        # Define text variables (tv) and boolean variables (bv), and
        # their associated entry (e) fields if applicable
        tv1 = StringVar()
        bv1_5 = BooleanVar()
        tv2 = StringVar()
        bv2_5 = BooleanVar()
        tv3 = StringVar()
        tv4 = StringVar()
        bv5_5 = BooleanVar()
        
        # Set defaults, for those that have them
        bv1_5.set(True)
        
        e1 = Entry(root, textvariable=tv1) 
        e2 = Entry(root, textvariable=tv2)
        e3 = Entry(root, textvariable=tv3)
        e4 = Entry(root, textvariable=tv4)
        
        # Place (grid) entry fields
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        e3.grid(row=2, column=1)
        e4.grid(row=4, column=1)
        
        # Define buttons
        b1 = Button(root, text='Choose', command = lambda: self.getOpenFileAndAutofill(tv1, tv3, tv4))
        b1_5 = Checkbutton(root, text ='Only check log within Prim8 data date range', var = bv1_5, onvalue = True, offvalue = False)
        b2 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv2))
        b2_5 = Checkbutton(root, text ="Don't blank this out after successful 'Go!'", var = bv2_5, onvalue = True, offvalue = False)
        b3 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv3))
        b4 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv4))
        b5 = Button(root, text='Go!', command = lambda: self.checkAndWriteSQL(tv1, bv1_5, tv2, bv2_5, tv3, tv4, bv5_5))
        b5_5 = Checkbutton(root, text ="Don't blank anything after successful 'Go!'", var = bv5_5, onvalue = True, offvalue = False)
        b6 = Button(root, text='Quit', command = lambda: self.endProgram(root))
        
        # Place (grid) buttons
        b1.grid(row=0, column=2, sticky='W', pady=4)
        b1_5.grid(row=0, column=3, sticky='W', pady=4)
        b2.grid(row=1, column=2, sticky='W', pady=4)
        b2_5.grid(row=1, column=3, sticky='W', pady=4)
        b3.grid(row=2, column=2, sticky='W', pady=4)
        b4.grid(row=4, column=2, sticky='W',pady=4)
        b5.grid(row=6, column=0, sticky='W',pady=4)
        b5_5.grid(row=6, column=3, sticky='W', pady=4)
        b6.grid(row=6, column=2, sticky='W',pady=4)
        
    
    def getOpenFileName(self, textVariable):
        '''
        Opens a dialog to ask for a file name to open.  Sets textVariable to
        hold the file's path (a string).
        '''
        filePath = askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='Choose a file:')
        print("Got file path:", filePath)
        textVariable.set(filePath)
    
    def getOpenFileAndAutofill(self, textVariable1, textVariable2, textVariable3):
        '''
        Just like "getOpenFileName", but also creates suggested file
        names and inserts them into textVariable2 and textVariable3.
        '''
        self.getOpenFileName(textVariable1)
        
        sourcePath = str(textVariable1.get())
        
        if len(sourcePath) > 0: # Only do the below if a file was selected
            summaryPath = sourcePath[:-4] + '_summary.txt' # So "./filename.txt" suggests "./filename_summary.txt"
            
            print("Suggesting summary file path:", summaryPath)
            textVariable2.set(summaryPath)
            
            sqlPath = sourcePath[:-4] + '_SQLout.sql' # So "./filename.txt" suggests "./filename_SQLout.sql"
            
            print("Suggesting SQL file path:", sqlPath)
            textVariable3.set(sqlPath)
    
    def endProgram(self, root):
        '''
        Ends the program.
        '''
        print("Closing program!")
        root.quit()
    
    def integrityCheck(self, inputFile, focalLogFile, limitLogDates, errorCheckedFile, outSQLFile):
        '''
        Input values are presumed to be the values given by the user in
        the GUI.  They should be actual strings/booleans/whatever, not
        StrVars/BooleanVars/WhateverVars.
        
        Makes sure all needed values have been entered and are not
        reused.
        
        Because file paths are chosen from a dialog, we don't do much
        to test their validity.
        
        Returns True if okay, False if not.
        '''
        allParams = [inputFile, limitLogDates, errorCheckedFile, outSQLFile]
        # Omit focalLogFile for now, because it doesn't actually need
        # to be provided
        
        # Make sure something was entered
        for item in allParams:
            strItem = str(item)
            if len(strItem) == 0:
                print("Missing value(s)!")
                return False
        
        # If limitLogDates is True, make sure we do have a log file
        if limitLogDates and len(focalLogFile) == 0:
            print("Limiting Log Dates, but no log file provided!")
            return False
        
        # Now add focalLogFile in
        allParams.append(focalLogFile)
        
        # Make sure inputs are unique
        setParams = set(allParams)
        return len(setParams) == len(allParams)
    
    def checkAndWriteSQL(self, inputFile, limitLogDates, focalLogFile, dontBlankLog, errorCheckedFile, outSQLFile, dontBlankAnything):
        '''
        The inputs should be the values added by the user in the GUI.
        
        After checking the integrity of the inputs, runs the
        errorChecking module, then the SQL-writing module.
        '''
        #Convert the StrVars to strings
        inFile = str(inputFile.get())
        logFile = str(focalLogFile.get())
        limitDates = limitLogDates.get()
        errorFile = str(errorCheckedFile.get())
        sqlFile = str(outSQLFile.get())
        
        noBlankLog = dontBlankLog.get()
        noBlankAnything = dontBlankAnything.get()
        
        if not self.integrityCheck(inFile, logFile, limitDates, errorFile, sqlFile):
            # The dontBlank___ things aren't included because there's
            # nothing to check related to them
            print("Problem with data! No work done.")
        else:
            errorCheck(inFile, errorFile, logFile, limitDates)
            sourceFileName = path.basename(inFile)
            outFileName = path.basename(errorFile)
            print("Finished writing summary of", sourceFileName, "to", outFileName)
            
            writeAll(inFile, sqlFile, True)
            sourceFileName = path.basename(inFile)
            outFileName = path.basename(sqlFile)
            print("Finished writing SQL from", sourceFileName, "to", outFileName)
            
            if not noBlankAnything:
                inputFile.set("") #Clear out file name
                errorCheckedFile.set("") #Clear out file name
                outSQLFile.set("") #Clear out file name
                if not noBlankLog:
                    focalLogFile.set("") #Clear out file name
            

if __name__=='__main__':
    myRoot = Tk()
    errorCheckingGUI(myRoot)
    myRoot.mainloop()
