'''
Created on 29 Sep 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

A GUI for processing data files into documents with SQL to add the data to Babase.
'''

from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from babaseWriter import writeAll
from os import path

class babaseWriterGUI(Frame):
    '''
    Create the GUI used for generating SQL from processed Prim8 data
    '''

    def __init__(self, root):
        '''
        Build the GUI.
        '''
        Frame.__init__(self, root)
        
        # Define labels
        l1 = Label(root, text="Processed prim8 data file:")
        l2 = Label(root, text="File to write SQL to:")
        l2a = Label(root, text="(autofilled)")
        
        # Place (grid) labels
        l1.grid(row=0)
        l2.grid(row=1)
        l2a.grid(row=2, column=1)
        
        # Define text variables (tv) and their associated entry (e) fields
        tv1 = StringVar()
        tv2 = StringVar()
        
        e1 = Entry(root, textvariable=tv1) 
        e2 = Entry(root, textvariable=tv2) 
        
        # Place (grid) entry fields
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        
        # Define buttons
        b1 = Button(root, text='Choose', command = lambda: self.getOpenFileAndAutofill(tv1, tv2))
        b2 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv2))
        b3 = Button(root, text='Go!', command = lambda: self.writeAllSQL(tv1,tv2))
        b4 = Button(root, text='Quit', command = lambda: self.endProgram(root))
        
        # Place (grid) buttons
        b1.grid(row=0, column=2, sticky='W', pady=4)
        b2.grid(row=1, column=2, sticky='W', pady=4)
        b3.grid(row=3, column=0, sticky='W',pady=4)
        b4.grid(row=3, column=1, sticky='W',pady=4)
        
    def getOpenFileName(self, textVariable):
        '''
        Opens a dialog to ask for a file name to open.  Sets textVariable to hold the file's path (a string).
        '''
        filePath = askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='Choose a file:')
        print "Got file path:", filePath
        textVariable.set(filePath)
    
    def getOpenFileAndAutofill(self, textVariable1, textVariable2):
        '''
        Just like "getOpenFileName", but also autofills a suggested output file name and inserts it in textVariable2.
        '''
        self.getOpenFileName(textVariable1)
        
        sourcePath = str(textVariable1.get())
        suggestedOutPath = sourcePath[:-4] + '_SQLout.sql' # So "./filename.txt" suggests "./filename_SQLout.sql"
        
        print "Suggesting SQL file path:", suggestedOutPath
        textVariable2.set(suggestedOutPath)
        
    def endProgram(self, root):
        '''
        Ends the program.
        '''
        print "Closing program!"
        root.quit()
        
    def integrityCheck(self, input1, input2):
        '''
        Input values are presumed to be the 2 values given by the user in the GUI.  They are assumed to be strings, not StrVars.
        
        Make sure all 2 entered values have been entered and are not identical.
        
        Because file paths are chosen from a dialog, we don't do much to test their validity.
        
        Returns True if okay, False if not.
        '''
        # Make sure something was entered
        for item in [input1, input2]:
            if len(item) == 0:
                print "Missing value(s)!"
                return False
                
        # Make sure the same input wasn't added twice
        return input1 != input2

    def writeAllSQL(self, input1, input2):
        '''
        The 2 inputs should be the 2 StrVar values added by the user in the GUI.
        
        After checking the integrity of the inputs, adds data about overlapping focals from the second file to the end of the first file.
        '''
        #Convert the StrVars to strings
        value1 = str(input1.get())
        value2 = str(input2.get())
        
        if not self.integrityCheck(value1, value2):
            print "Problem with data! No work done."
        else:
            writeAll(value1, value2, True)
            sourceFileName = path.basename(value1)
            outFileName = path.basename(value2)
            print "Finished writing SQL from", sourceFileName, "to", outFileName
            
            input1.set("") #Clear out file name
            input2.set("") #Clear out file name
        
if __name__=='__main__':
    myRoot = Tk()
    babaseWriterGUI(myRoot)
    myRoot.mainloop()