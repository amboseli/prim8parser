'''
Created on 8 Sep 2015

GUI to use for processing of data exported from Prim8

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''

from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from constants import prim8Name, prim8Version, prim8Setup
from cleanRawFile import makeAllDicts, writeAll

class rawFileImportGUI(Frame):
    '''
    Builds the GUI used for processing raw Prim8 data into files readable by humans 
    '''

    def __init__(self, root):
        '''
        Start the GUI.
        '''
        Frame.__init__(self, root)
        
        # Define labels
        l1 = Label(root, text="Import file:")
        l2 = Label(root, text="Export file:")
        l3 = Label(root, text="App used to collect data:")
        l4 = Label(root, text="App version number:")
        l5 = Label(root, text="App setup name:")
        l6 = Label(root, text="Tablet ID:")
        
        # Place (grid) labels
        l1.grid(row=0)
        l2.grid(row=1)
        l3.grid(row=2)
        l4.grid(row=3)
        l5.grid(row=4)
        l6.grid(row=5)

        # Define text variables (tv) and their associated entry (e) fields
        tv1 = StringVar()
        tv2 = StringVar()
        tv3 = StringVar()
        tv4 = StringVar()
        tv5 = StringVar()
        tv6 = StringVar()

        tv3.set(prim8Name)
        tv4.set(prim8Version)
        tv5.set(prim8Setup)        
        
        e1 = Entry(root, textvariable=tv1) 
        e2 = Entry(root, textvariable=tv2) 
        e3 = Entry(root, textvariable=tv3)
        e4 = Entry(root, textvariable=tv4) 
        e5 = Entry(root, textvariable=tv5)
        e6 = Entry(root, textvariable=tv6) 
        
        # Place (grid) entry fields
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        e3.grid(row=2, column=1)
        e4.grid(row=3, column=1)
        e5.grid(row=4, column=1)
        e6.grid(row=5, column=1)
                
        # Define buttons
        b1 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv1))
        b2 = Button(root, text='Choose', command = lambda: self.getSaveFileName(tv2, tv6))
        b3 = Button(root, text='Import', command = lambda: self.compileData(tv1,tv2,tv3,tv4,tv5,tv6))
        b4 = Button(root, text='Close', command = lambda: self.endProgram(root))
        
        # Place (grid) buttons
        b1.grid(row=0, column=2, sticky='W', pady=4)
        b2.grid(row=1, column=2, sticky='W', pady=4)
        b3.grid(row=6, column=0,sticky='W', pady=4)
        b4.grid(row=6, column=1, sticky='W',pady=4)
        
    def getOpenFileName(self, textVariable):
        '''
        Opens a dialog to ask for a file name to open.  Sets textVariable to hold the file's path (a string).
        '''
        filePath = askopenfilename(filetypes=(('Comma-separated','*.csv'),('All files','*.*')), title='Select a file to import:')
        print "Got file path:", filePath
        textVariable.set(filePath)
    
    def guessTabletID(self, filePath, textVariable):
        '''
        filePath is a string and a file path, presumably for the file that is written-to in this GUI.
            Its last 6 characters will likely be '[2-character tablet ID].txt'.
        Given filePath, inserts the 2 characters representing the tablet ID into textVariable.
        '''
        tabletID = filePath[-6:-4]
        print "Tablet ID predicted to be", tabletID 
        textVariable.set(tabletID)
        
    
    def getSaveFileName(self, textVariableSaveFile, textVariableTabletID):
        '''
        Opens a dialog to ask for a file name to save/replace.  Sets textVariableSaveFile to hold the file's path (a string).
        
        Also makes a prediction of the tablet ID, based on the name of the saved file.
        '''
        filePath = asksaveasfilename(defaultextension='.txt', title='Name of the data file to create and write to?')
        print "Got output file path:", filePath
        textVariableSaveFile.set(filePath)
        self.guessTabletID(filePath, textVariableTabletID)
        
    def endProgram(self, root):
        '''
        Ends the program.
        '''
        print "Closing program!"
        root.quit()
        
    def integrityCheck(self, input1, input2, input3, input4, input5, input6):
        '''
        Input values should be the values given by the user in the GUI.  They are assumed to be strings, not StrVars.
        
        Make sure all entered values have been entered and are logical.
        
        Because file paths are chosen from a dialog, we won't do much here to test their validity.
        
        It would probably be preferable to actually check Babase to make sure that the programid and setupid are allowed.
            For now, this does not happen.
        
        Returns True if okay, False if not.
        '''
        # Make sure something was entered
        for item in [input1, input2, input3, input4, input5, input6]:
            if len(item) == 0:
                print "Missing value(s)!"
                return False
        return True

    def compileData(self, input1, input2, input3, input4, input5, input6):
        '''
        The inputs should be the StrVar values added by the user in the GUI.
        
        After checking the integrity of the parameters, combines the agonisms from the two files and rewrites them in the first file.
        '''
        #Convert the StrVars to strings
        value1 = str(input1.get())
        value2 = str(input2.get())
        value3 = str(input3.get())
        value4 = str(input4.get())
        value5 = str(input5.get())
        value6 = str(input6.get())
        
        if not self.integrityCheck(value1, value2, value3, value4, value5, value6):
            print "Problem with data! No work done."
        else:
            allData = makeAllDicts(value1)
            print writeAll(value2, value3, value4, value5, value6, allData)
            # Empty fields to ensure the same file and tablet ID aren't accidentally used twice
            input1.set("")
            input2.set("")
            input6.set("")
            
if __name__=='__main__':
    myRoot = Tk()
    rawFileImportGUI(myRoot)
    myRoot.mainloop()