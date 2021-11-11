'''
Created on 2 Sep 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from gatherAgonisms import gatherAgonisms
from datetime import datetime

class gatherAgsGUI(Frame):
    '''
    Create the GUI that will be used by the "gatherAgonisms" program to compile all the agonisms for a period of time (presumably a month).
    '''
    def __init__(self, root):
        '''
        Build the GUI.
        '''
        Frame.__init__(self, root)
        
        # Define labels
        l1 = Label(root, text="File of agonisms compiled so far:")
        l2 = Label(root, text="Data to add:")
        l3 = Label(root, text="Minimum date of interactions? (yyyy-mm-dd)")
        l4 = Label(root, text="Maximum date of interactions? (yyyy-mm-dd)")
        
        # Place (grid) labels
        l1.grid(row=0)
        l2.grid(row=1)
        l3.grid(row=2)
        l4.grid(row=3)
        
        # Define text variables (tv) and their associated entry (e) fields
        tv1 = StringVar()
        tv2 = StringVar()
        tv3 = StringVar()
        tv4 = StringVar()
        
        e1 = Entry(root, textvariable=tv1) 
        e2 = Entry(root, textvariable=tv2) 
        e3 = Entry(root, textvariable=tv3)
        e4 = Entry(root, textvariable=tv4)
        
        # Place (grid) entry fields
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        e3.grid(row=2, column=1)
        e4.grid(row=3, column=1)
        
        # Define buttons
        b1 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv1))
        b2 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv2))
        b3 = Button(root, text='Accept', command = lambda: self.compileAgonisms(tv1,tv2,tv3,tv4))
        b4 = Button(root, text='Close', command = lambda: self.endProgram(root))
        
        # Place (grid) buttons
        b1.grid(row=0, column=2, sticky='W', pady=4)
        b2.grid(row=1, column=2, sticky='W', pady=4)
        b3.grid(row=4, sticky='W',pady=4)
        b4.grid(row=4, column=1, sticky='W',pady=4)
    
    def getOpenFileName(self, textVariable):
        '''
        Opens a dialog to ask for a file name to open.  Sets textVariable to hold the file's path (a string).
        '''
        filePath = askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='File of agonisms so far:')
        print("Got file path:", filePath)
        textVariable.set(filePath)
    
    def endProgram(self, root):
        '''
        Ends the program.
        '''
        root.quit()
    
    def integrityCheck(self, input1, input2, input3, input4):
        '''
        Input values are presumed to be the 4 values given by the user in the GUI.  They are assumed to be strings, not StrVars.
        
        Make sure all 4 entered values have been entered and are logical.
        
        Because file paths are chosen from a dialog, we won't do much here to test their validity.
        
        Returns True if okay, False if not.
        '''
        # Make sure something was entered
        for item in [input1, input2, input3, input4]:
            if len(item) == 0:
                print("Missing value(s)!")
                return False
        
        # Make sure dates are in the right format
        for date in (input3, input4):
            try:
                testDate = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                print("Date(s) in incorrect format! Need yyyy-mm-dd.")
                return False
        
        # Make sure the date in tv4 is greater than tv3
        return input4 > input3
    
    def compileAgonisms(self, input1, input2, input3, input4):
        '''
        The 4 inputs should be the 4 StrVar values added by the user in the GUI.
        
        After checking the integrity of the 4 values, combines the agonisms from the two files and rewrites them in the first file.
        '''
        #Convert the StrVars to strings
        value1 = str(input1.get())
        value2 = str(input2.get())
        value3 = str(input3.get())
        value4 = str(input4.get())
        
        if not self.integrityCheck(value1, value2, value3, value4):
            print("Problem with data! No work done.")
        else:
            gatherAgonisms(value1, value2, value3, value4)
            #This function prints success/error messages to console, so no need to add one here

if __name__=='__main__':
    myRoot = Tk()
    gatherAgsGUI(myRoot)
    myRoot.mainloop()
