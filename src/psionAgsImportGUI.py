'''
Created on 10 Sep 2015

GUI for pulling agonisms from Psion data into a format usable by the agonism compiler.

@author: Jake Gordon, <jacob.b.gordon@gmail.com>
'''

from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from getPsionAgs import getPsionAgonisms


class psionAgsImportGUI(Frame):
    '''
    Builds the GUI used for pulling and processing agonisms from Psion data 
    '''

    def __init__(self, root):
        '''
        Start the GUI.
        '''
        Frame.__init__(self, root)
        
        # Define labels
        l1 = Label(root, text="Psion data file:")
        l2 = Label(root, text="New export file:")
        
        # Place (grid) labels
        l1.grid(row=0)
        l2.grid(row=1)
        
        # Define text variables (tv) and their associated entry (e) fields
        tv1 = StringVar()
        tv2 = StringVar()
        
        e1 = Entry(root, textvariable=tv1) 
        e2 = Entry(root, textvariable=tv2) 
        
        # Place (grid) entry fields
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        
        # Define buttons
        b1 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv1))
        b2 = Button(root, text='Choose', command = lambda: self.getSaveFileName(tv2))
        b3 = Button(root, text='Import', command = lambda: self.compileData(tv1,tv2))
        b4 = Button(root, text='Close', command = lambda: self.endProgram(root))
        
        # Place (grid) buttons
        b1.grid(row=0, column=2, sticky='W', pady=4)
        b2.grid(row=1, column=2, sticky='W', pady=4)
        b3.grid(row=2, column=0,sticky='W', pady=4)
        b4.grid(row=2, column=1, sticky='W',pady=4)
        
    def getOpenFileName(self, textVariable):
        '''
        Opens a dialog to ask for a file name to open.  Sets textVariable to hold the file's path (a string).
        '''
        filePath = askopenfilename(filetypes=(('Psion data file','*.pts'),('All files','*.*')), title='Select a Psion file to import:')
        print "Got Psion file path:", filePath
        textVariable.set(filePath)
    
    def getSaveFileName(self, textVariable):
        '''
        Opens a dialog to ask for a file name to save/replace.  Sets textVariable to hold the file's path (a string).
        '''
        filePath = asksaveasfilename(defaultextension='.txt', title='Name of the data file to create and write to?')
        print "Got output file path:", filePath
        textVariable.set(filePath)
        
    def endProgram(self, root):
        '''
        Ends the program.
        '''
        print "Closing program!"
        root.quit()
        
    def integrityCheck(self, input1, input2):
        '''
        Input values should be the values given by the user in the GUI.  They are assumed to be strings, not StrVars.
        
        Make sure all entered values have been entered and are logical.
        
        Because file paths are chosen from a dialog, we won't do much here to test their validity.
        
        Returns True if okay, False if not.
        '''
        # Make sure something was entered
        for item in [input1, input2]:
            if len(item) == 0:
                print "Missing value(s)!"
                return False
        
        # Make sure the two inputs aren't identical
        if input1[:] == input2[:]:
            print "Input and output files can't be the same thing!"
            return False
        
        else:
            return True

    def compileData(self, input1, input2):
        '''
        The inputs should be the StrVar values added by the user in the GUI.
        
        After checking the integrity of the parameters, combines the agonisms from the two files and rewrites them in the first file.
        '''
        #Convert the StrVars to strings
        value1 = str(input1.get())
        value2 = str(input2.get())
        
        if not self.integrityCheck(value1, value2):
            print "Problem with data! No work done."
        else:
            getPsionAgonisms(value1, value2)
            #Empty both fields to help prevent using or saving over the same file
            input1.set("")
            input2.set("")
            
            
if __name__=='__main__':
    myRoot = Tk()
    psionAgsImportGUI(myRoot)
    myRoot.mainloop()