'''
Created on 3 June 2019

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

A GUI for checking data files for errors/alerts, specifically focused on
generating feedback for the field team.

Shamelessly adapted from the errorCheckingGUI class.
'''

from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from observerFeedback import makeFeedback
from os import path

class observerFeedbackGUI(Frame):
    '''
    Create the GUI used for generating observer feedback.
    '''
    
    def __init__(self, root):
        '''
        Build the GUI.
        '''
        Frame.__init__(self, root)
        
        # Define labels
        l1 = Label(root, text="Processed prim8 data file:")
        l2 = Label(root, text="Focal sample log file (optional):")
        l3 = Label(root, text="File to write feedback to:")
        l3a = Label(root, text="(autofilled)")
        
        # Place (grid) labels
        l1.grid(row=0)
        l2.grid(row=1)
        l3.grid(row=2)
        l3a.grid(row=3, column = 1)
        
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
        e3.grid(row=2, column=1)
        
        # Define buttons
        b1 = Button(root, text='Choose', command = lambda: self.getOpenFileAndAutofill(tv1, tv3))
        b2 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv2))
        b3 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv3))
        b4 = Button(root, text='Go!', command = lambda: self.doTheFeedback(tv1, tv2, tv3))
        b5 = Button(root, text='Quit', command = lambda: self.endProgram(root))
        
        # Place (grid) buttons
        b1.grid(row=0, column=2, sticky='W', pady=4)
        b2.grid(row=1, column=2, sticky='W', pady=4)
        b3.grid(row=2, column=2, sticky='W', pady=4)
        b4.grid(row=4, column=0, sticky='W',pady=4)
        b5.grid(row=4, column=1, sticky='W',pady=4)
    
    def getOpenFileName(self, textVariable):
        '''
        Opens a dialog to ask for a file name to open.  Sets textVariable to
        hold the file's path (a string).
        '''
        filePath = askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='Choose a file:')
        print("Got file path:", filePath)
        textVariable.set(filePath)
    
    def getOpenFileAndAutofill(self, textVariable1, textVariable2):
        '''
        Just like "getOpenFileName", but also suggests a file name and
        inserts it into textVariable2.
        '''
        self.getOpenFileName(textVariable1)
        
        sourcePath = str(textVariable1.get())
        summaryPath = sourcePath[:-4] + '_feedback.txt' # So "./filename.txt" suggests "./filename_feedback.txt"
        
        print("Suggesting summary file path:", summaryPath)
        textVariable2.set(summaryPath)
        
    
    def endProgram(self, root):
        '''
        Ends the program.
        '''
        print("Closing program!")
        root.quit()
    
    def integrityCheck(self, inputFile, focalLogFile, errorCheckedFile):
        '''
        Input values are presumed to be the values given by the user in
        the GUI.  They are assumed to be strings, not StrVars.
        
        Make sure all needed values have been entered and are not
        reused.
        
        Because file paths are chosen from a dialog, we don't do much
        to test their validity.
        
        Returns True if okay, False if not.
        '''
        allParams = [inputFile, errorCheckedFile]
        # Omit focalLogFile for now, because it doesn't actually need
        # to be provided
        
        # Make sure something was entered
        for item in allParams:
            if len(item) == 0:
                print("Missing value(s)!")
                return False
        
        # Now add focalLogFile in
        allParams.append(focalLogFile)
        
        # Make sure inputs are unique
        setParams = set(allParams)
        return len(setParams) == len(allParams)
    
    def doTheFeedback(self, inputFile, focalLogFile, errorCheckedFile):
        '''
        The inputs should be the StrVar values added by the user in the
        GUI.
        
        After checking the integrity of the inputs, runs the
        observerFeedback module.
        '''
        #Convert the StrVars to strings
        inFile = str(inputFile.get())
        logFile = str(focalLogFile.get())
        errorFile = str(errorCheckedFile.get())
                
        if not self.integrityCheck(inFile, logFile, errorFile):
            print("Problem with data! No work done.")
        else:
            makeFeedback(inFile, errorFile, logFile)
            sourceFileName = path.basename(inFile)
            outFileName = path.basename(errorFile)
            print("Finished writing summary of", sourceFileName, "to", outFileName)
                        
            #inputFile.set("") #Clear out file name
            #focalLogFile.set("") #Clear out file name
            #errorCheckedFile.set("") #Clear out file name
        

if __name__=='__main__':
    myRoot = Tk()
    observerFeedbackGUI(myRoot)
    myRoot.mainloop()
