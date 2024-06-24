'''
Created on 25 Sep 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

Functions that return strings of SQL that can be used in Babase.
'''

def lookupGroupNum_SQL(threeLtrGrp):
    '''
    threeLtrGrp is a string, the 3-letter code used in the data to refer to a group's name.
    
    Returns a string: the SQL used to look up the 3-letter code and return the corresponding grp number (GROUPS.Gid).
        The SQL is wrapped in parentheses, because this will only ever be used as a subquery.
    '''
    grpNumLookUp = '''
                (SELECT gid FROM babase.groups WHERE three_letter_code='{0}')'''.format(threeLtrGrp)
    return grpNumLookUp

def lookupProgramID_SQL(pid_string):
    '''
    pid_string is a string, and should be a PROGRAMIDS.Pid_string value.
    
    Returns a string: the SQL to look up the PROGRAMIDS.Programid for pid_string.
        The SQL is wrapped in parentheses, because this will only ever be used as a subquery.
    '''
    progIDLookUp = '''
                (SELECT programid FROM babase.programids where pid_string='{0}')'''.format(pid_string)
    return progIDLookUp

def lookupSetupID_SQL(sid_string):
    '''
    sid_string is a string, and should be a SETUPIDS.Sid_string value.
    
    Returns a string: the SQL to look up the SETUPIDS.Setupid for sid_string.
        The SQL is wrapped in parentheses, because this will only ever be used as a subquery.
    '''
    setupIDLookUp = '''
                (SELECT setupid FROM babase.setupids where sid_string='{0}')'''.format(sid_string)
    return setupIDLookUp

def lookupCollection_System_SQL(descr):
    '''
    descr is a string, and should be a SAMPLES_COLLECTION_SYSTEMS.Descr value.
    
    Returns a string: the SQL to look up the SAMPLES_COLLECTION_SYSTEMS.Collection_System for descr.
        The SQL is wrapped in parentheses, because this will only ever be used as a subquery.
    '''
    collection_systemLookUp = '''
                (SELECT collection_system FROM babase.samples_collection_systems where descr='{0}')'''.format(descr)
    return collection_systemLookUp

def insertSAMPLES_SQL(date, stime, observer, stype, grp, sname, mins, programid, setupid, collection_system):
    '''
    All parameters are strings, and they indicate values to be added to columns of the same name.
    
    Returns a string: an SQL "insert" command to add a line to the SAMPLES table in Babase.
        Note that the returned string does not include quotation marks for the following values:
            1) grp (it's a number)
            2) mins (it's an integer)
            3) programid (this will contain a subquery)
            4) setupid (this will contain a subquery)
            5) collection_system (this will contain a subquery)
    '''
    insLine = '''
        INSERT INTO babase.samples(date, stime, observer, stype, grp, sname, mins, programid, setupid, collection_system)
            VALUES('{0}','{1}','{2}','{3}',{4},'{5}',{6},{7},{8}, {9});
    '''.format(date, stime, observer, stype, grp, sname, mins, programid, setupid, collection_system)
    print(insLine)
    return insLine

def insertPOINT_DATA_SQL(pntMin, activity, posture, ptime, foodcode=''):
    '''
    All parameters are strings, and they indicate values to be added to columns of the same name.
        One exception: pntMin refers to the POINT_DATA.Min column. "min" is reserved by Python.
        
    If the point to be added does not have a foodcode, it should be omitted from the parameters.
    
    Returns a string: an SQL "insert" command to add a line to the POINT_DATA table in Babase.
        Note that the returned string does not include quotation marks around the pntMin value, 
        because the corresponding Babase column is a smallint.
    '''
    insLine = ''
    
    if foodcode =='':
        insLine = '''
        INSERT INTO babase.point_data(sid, min, activity, posture, ptime)
            VALUES((SELECT currval('samples_sid_seq'::regclass)), {0}, '{1}', '{2}', '{3}');
        '''.format(pntMin, activity, posture, ptime)
    else:
        insLine = '''
        INSERT INTO babase.point_data(sid, min, activity, posture, ptime, foodcode)
            VALUES((SELECT currval('samples_sid_seq'::regclass)), {0}, '{1}', '{2}', '{3}', '{4}');
        '''.format(pntMin, activity, posture, ptime, foodcode)
    
    print(insLine)
    return insLine

def insertFPOINTS_SQL(kidcontact, kidsuckle):
    '''
    All parameters are strings, and they indicate values to be added to columns of the same name.
    
    Returns a string: an SQL "insert" command to add a line to the FPOINTS table in Babase.
    '''
    insLine = '''
        INSERT INTO babase.fpoints(pntid, kidcontact, kidsuckle)
            VALUES((SELECT currval('point_data_pntid_seq'::regclass)), '{0}', '{1}');
    '''.format(kidcontact, kidsuckle)
    print(insLine)
    return insLine

def insertNEIGHBORS_SQL(neighborID, ncode):
    '''
    Both parameters are strings, and they indicate values to be added to columns in the NEIGHBORS table:
        ncode gets added to the ncode column.
        neighborID gets added to either the sname column or the unksname column, but not both.
    
    If neighborID is one of the allowed "unknown" snames, it gets added to the unksname column.  Otherwise,
        it's presumed to be a real sname.
    
    Returns a string: an SQL "insert" command to add a line to the NEIGHBORS table in Babase.
    '''
    from constants import unknSnames
    
    insLine = ''
    
    if neighborID in unknSnames:
        insLine = '''
        INSERT INTO babase.neighbors(pntid, ncode, unksname)
            VALUES((SELECT currval('point_data_pntid_seq'::regclass)), '{0}', '{1}');
        '''.format(ncode, unknSnames[neighborID])
    else:
        insLine = '''
        INSERT INTO babase.neighbors(pntid, ncode, sname)
            VALUES((SELECT currval('point_data_pntid_seq'::regclass)), '{0}', '{1}');
        '''.format(ncode, neighborID)
    
    print(insLine)
    return insLine

def insertACTOR_ACTEES_SQL(inFocal, observer, date, start, actor, act, actee, handwritten='FALSE'):
    '''
    inFocal is a boolean indicating whether or not the behavior occurred during a focal sample.
    All other parameters are strings, and they indicate values to be added to columns of the same name.
        One exception: the "start" value here is used in the "Start" and "Stop" columns.
        
    Whether or not the behavior occurred during a focal sample affects which columns are inserted.
        Specifically, if during a focal, we insert data into the Sid, Start, and Stop columns of
        ACTOR_ACTEES.
    
    NOTE: As of this writing (28 Sep 2015), any data to be stored in ACTOR_ACTEES and collected 
        in Prim8 but not during a focal sample will also NOT have its timepoint saved.  This
        decision was made because
            1) that's currently a rule in ACTOR_ACTEES anyway, leftover from the Psion era
            2) we're not certain that the observers will always record interactions precisely when
                they were observed, so we don't want timestamps to imply more confidence than we
                actually have.
        
    Returns a string: an SQL "insert" command to add a line to the ACTOR_ACTEES view in Babase.
    '''
    insLine = ''
    
    if inFocal:
        insLine = '''
        INSERT INTO babase.actor_actees(sid, observer, date, start, stop, actor, act, actee, handwritten)
            VALUES((SELECT currval('samples_sid_seq'::regclass)), '{0}', '{1}', '{2}', '{2}', '{3}', '{4}', '{5}', {6});
        '''.format(observer, date, start, actor, act, actee, handwritten)
    else:
        insLine = '''
        INSERT INTO babase.actor_actees(observer, date, actor, act, actee, handwritten)
            VALUES('{0}', '{1}', '{2}', '{3}', '{4}', {5});
        '''.format(observer, date, actor, act, actee, handwritten)
    print(insLine)
    return insLine

def insertALLMISCS_SQL(atime, txtPrefix, txt):
    '''
    atime and txt are strings, and they indicate values to be added to columns
    of the same name.  txtPrefix is a special value added to txt and required by
    Babase:
    
    An artifact of the previous technology, the ALLMISCS.txt column requires
    that every field begin with a one-character code that indicates what kind of
    note is being made, then a comma.  For example:
        BAD: "Missed point because reasons"
        GOOD: "O, Missed point because reasons"
        (In this example, the "O" stands for "other")
    
    Returns a string: an SQL "insert" command to add a line to the ALLMISCS
    table in Babase.
    '''
    fullText = txtPrefix + ',' + txt
    
    insLine = '''
        INSERT INTO babase.allmiscs(sid, atime, txt)
            VALUES((SELECT currval('samples_sid_seq'::regclass)), '{0}', '{1}');
    '''.format(atime, fullText)
    print(insLine)
    return insLine

def selectThisLine(dataLine):
    '''
    Returns a "select [dataLine];" string. In case there's an error or issue
    during import to Babase, this helps make it clear which statement is causing
    the trouble.
    
    dataLine is a list of strings. It is joined together and tab-delimited
    before being written in the returned "select" statement.
    '''
    from babaseWriteHelpers import sqlizeApostrophes
    
    thisLine = sqlizeApostrophes('\t'.join(dataLine))
    selLine = '''
        SELECT '{0}' as line;
    '''.format(thisLine)
    
    print(selLine)
    return selLine
