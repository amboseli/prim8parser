'''
Created on 16 Nov 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

A GUI for checking data files for errors and potentially-problematic events.

Adapted from the babaseWriterGUI.
'''

from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
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
        l2 = Label(root, text="File to write summary to:")
        l2a = Label(root, text="(autofilled)")
        l3 = Label(root, text="File to write SQL to:")
        l3a = Label(root, text="(autofilled)")
        
        # Place (grid) labels
        l1.grid(row=0)
        l2.grid(row=1)
        l2a.grid(row=2, column = 1)
        l3.grid(row=3)
        l3a.grid(row=4, column = 1)
        
        # Define text variables (tv) and their associated entry (e) fields
        tv1 = StringVar()
        tv2 = StringVar()
        tv3 = StringVar()
        
        e1 = Entry(root, textvariable=tv1) 
        e2 = Entry(root, textvariable=tv2)
        e3 = Entry(root, textvariable=tv3) 
        
        # Place (grid) entry fields
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        e3.grid(row=3, column=1)
        
        # Define buttons
        b1 = Button(root, text='Choose', command = lambda: self.getOpenFileAndAutofill(tv1, tv2, tv3))
        b2 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv2))
        b3 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv3))
        b4 = Button(root, text='Go!', command = lambda: self.checkAndWriteSQL(tv1,tv2,tv3))
        b5 = Button(root, text='Quit', command = lambda: self.endProgram(root))
        
        # Place (grid) buttons
        b1.grid(row=0, column=2, sticky='W', pady=4)
        b2.grid(row=1, column=2, sticky='W', pady=4)
        b3.grid(row=3, column=2, sticky='W', pady=4)
        b4.grid(row=5, column=0, sticky='W',pady=4)
        b5.grid(row=5, column=1, sticky='W',pady=4)
    
    def getOpenFileName(self, textVariable):
        '''
        Opens a dialog to ask for a file name to open.  Sets textVariable to
        hold the file's path (a string).
        '''
        filePath = askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='Choose a file:')
        print "Got file path:", filePath
        textVariable.set(filePath)
    
    def getOpenFileAndAutofill(self, textVariable1, textVariable2, textVariable3):
        '''
        Just like "getOpenFileName", but also creates suggested file
        names and inserts them into textVariable2 and textVariable3.
        '''
        self.getOpenFileName(textVariable1)
        
        sourcePath = str(textVariable1.get())
        summaryPath = sourcePath[:-4] + '_summary.txt' # So "./filename.txt" suggests "./filename_summary.txt"
        
        print "Suggesting summary file path:", summaryPath
        textVariable2.set(summaryPath)
        
        sqlPath = sourcePath[:-4] + '_SQLout.sql' # So "./filename.txt" suggests "./filename_SQLout.sql"
        
        print "Suggesting SQL file path:", sqlPath
        textVariable3.set(sqlPath)
    
    def endProgram(self, root):
        '''
        Ends the program.
        '''
        print "Closing program!"
        root.quit()
    
    def integrityCheck(self, input1, input2, input3):
        '''
        Input values are presumed to be the 3 values given by the user in the GUI.  They are assumed to be strings, not StrVars.
        
        Make sure all 3 values have been entered and are not identical.
        
        Because file paths are chosen from a dialog, we don't do much to test their validity.
        
        Returns True if okay, False if not.
        '''
        allParams = [input1, input2, input3]
        
        # Make sure something was entered
        for item in allParams:
            if len(item) == 0:
                print "Missing value(s)!"
                return False
                
        # Make sure inputs are unique
        setParams = set(allParams)
        return len(setParams) == len(allParams)
    
    def checkAndWriteSQL(self, input1, input2, input3):
        '''
        The inputs should be the 3 StrVar values added by the user in the GUI.
        
        After checking the integrity of the inputs, runs the errorChecking
        module, then the SQL-writing module.
        '''
        #Convert the StrVars to strings
        value1 = str(input1.get())
        value2 = str(input2.get())
        value3 = str(input3.get())
        
        if not self.integrityCheck(value1, value2, value3):
            print "Problem with data! No work done."
        else:
            errorCheck(value1, value2)
            sourceFileName = path.basename(value1)
            outFileName = path.basename(value2)
            print "Finished writing summary of", sourceFileName, "to", outFileName
            
            writeAll(value1, value3, True)
            sourceFileName = path.basename(value1)
            outFileName = path.basename(value3)
            print "Finished writing SQL from", sourceFileName, "to", outFileName
            
            input1.set("") #Clear out file name
            input2.set("") #Clear out file name
            input3.set("") #Clear out file name

if __name__=='__main__':
    myRoot = Tk()
    errorCheckingGUI(myRoot)
    myRoot.mainloop()