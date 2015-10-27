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

def lookupPalmtop_SQL(descr):
    '''
    descr is a string, and should be a PALMTOPS.Descr value.
    
    Returns a string: the SQL to look up the PALMTOPS.Palmtop for descr.
        The SQL is wrapped in parentheses, because this will only ever be used as a subquery.
    '''
    palmtopLookUp = '''
                (SELECT palmtop FROM babase.palmtops where descr='{0}')'''.format(descr)
    return palmtopLookUp

def insertSAMPLES_SQL(date, stime, observer, stype, grp, sname, mins, programid, setupid, palmtop):
    '''
    All parameters are strings, and they indicate values to be added to columns of the same name.
    
    Returns a string: an SQL "insert" command to add a line to the SAMPLES table in Babase.
        Note that the returned string does not include quotation marks for the following values:
            1) grp (it's a number)
            2) mins (it's an integer)
            3) programid (this will contain a subquery)
            4) setupid (this will contain a subquery)
            5) palmtop (this will contain a subquery)
    '''
    insLine = '''
        INSERT INTO babase.samples(date, stime, observer, stype, grp, sname, mins, programid, setupid, palmtop)
            VALUES('{0}','{1}','{2}','{3}',{4},'{5}',{6},{7},{8}, {9});
    '''.format(date, stime, observer, stype, grp, sname, mins, programid, setupid, palmtop)
    print insLine
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
    
    print insLine
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
    print insLine
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
    
    print insLine
    return insLine

def insertACTOR_ACTEES_SQL(inFocal, observer, date, start, actor, act, actee):
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
        INSERT INTO babase.actor_actees(sid, observer, date, start, stop, actor, act, actee)
            VALUES((SELECT currval('samples_sid_seq'::regclass)), '{0}', '{1}', '{2}', '{2}', '{3}', '{4}', '{5}');
        '''.format(observer, date, start, actor, act, actee)
    else:
        insLine = '''
        INSERT INTO babase.actor_actees(observer, date, actor, act, actee)
            VALUES('{0}', '{1}', '{2}', '{3}', '{4}');
        '''.format(observer, date, actor, act, actee)
    print insLine
    return insLine

def insertALLMISCS_SQL(atime, txt):
    '''
    All parameters are strings, and they indicate values to be added to columns of the same name.
    
    Returns a string: an SQL "insert" command to add a line to the ALLMISCS table in Babase.
    '''
    from constants import allMiscsPrefix
    
    insLine = '''
        INSERT INTO babase.allmiscs(sid, atime, txt)
            VALUES((SELECT currval('samples_sid_seq'::regclass)), '{0}', '{1}');
    '''.format(atime, allMiscsPrefix + txt)
    print insLine
    return insLine
