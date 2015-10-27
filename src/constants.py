'''
Created on 4 Sep 2015

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

Constants used throughout the parser.

'''
# Codes NOT in Prim8
    # 'ADL', for example, IS in Prim8, so it's not listed here.
focalAbbrev = 'HDR' ##Abbreviation for output file to indicate that the line begins a new focal sample
neighborAbbrev = 'NGH' ##Abbreviation for output file to indicate that the line is a focal neighbor
noteAbbrev = 'TXT' ##Abbreviation for output file to indicate that the line is freeform text
emptyAbbrev = 'NULL'

# Codes in Prim8 that may change
adlibAbbrev = 'ADL'
pntAbbrev = 'PNT'
proxBehavName = 'proximity'
outOfSightValue = 'OOS'

# Tables in the main Prim8 data file.
# These NEED to be spelled the same way as they are in the file. Case sensitive.
p8adlib = 'adlib'
p8sites = 'sites'
p8observers = 'observers'
p8groups = 'groups'
p8species = 'species'
p8individuals = 'individuals'
p8biologicalsamples = 'biologicalsamples'
p8coordinatesystem = 'coordinatesystem'
p8locations = 'locations'
p8workcalendars = 'workcalendars'
p8behaviortypes = 'behaviortypes'
p8behaviors = 'behaviors'
p8focalfollows = 'focalfollows'
p8scans = 'scans'
p8behaviorinstances = 'behaviorinstances'
p8focalbehaviors = 'focalbehaviors'
p8scanbehaviors = 'scanbehaviors'
p8modifiers = 'modifiers'
dictInstMods = 'instances_modifiers' #Not in prim8 data, but during import we create this extra table/dictionary and save it with the rest

# Order in this list is NOT important.
p8TableList = [p8adlib, p8sites, p8observers, p8groups, p8species, p8individuals, p8biologicalsamples, p8coordinatesystem, p8locations, p8workcalendars, p8behaviortypes, p8behaviors, p8focalfollows, p8scans, p8behaviorinstances, p8focalbehaviors, p8scanbehaviors, p8modifiers] 

# Tables whose lines represent observations that we want to retain
observationTables = [p8adlib, p8behaviorinstances, p8focalfollows]

# Info about the current Prim8 version
prim8Name = 'AMBOPRIM8'
prim8Version = '1.150728'
prim8Setup = 'JUL15' # Used to populate the "setupid" in babase. The name "setup" made more sense for Psion data. It makes less sense for Prim8.

# Dictionary with abbreviations for all the tablets in use and their descriptions in Babase (PALMTOPS.Descr)
palmtops = {}
palmtops['SA'] = 'Samsung Tablet A'
palmtops['SB'] = 'Samsung Tablet B'
palmtops['SC'] = 'Samsung Tablet C'
palmtops['SD'] = 'Samsung Tablet D'

# Used when compiling agonisms
agonismCodes = ['AS', 'OS', 'DS']

# Neighbor codes used in Prim8, and their Babase counterparts
neighborsFem = {}
neighborsFem['N0'] = '1'
neighborsFem['N1'] = 'A'
neighborsFem['N2'] = 'O'

neighborsJuv = {}
neighborsJuv['N0'] = '1'
neighborsJuv['N1'] = '2'
neighborsJuv['N2'] = '3'

# Unknown neighbor snames used in Prim8, and their Babase counterparts
unknSnames = {}
unknSnames['997'] = '997'
unknSnames['998'] = '998'
unknSnames['XXX'] = 'NULL'

# Codes representing focal sample "types" (adult females vs. juveniles)
stypeAdultFem = 'FEM'
stypeJuv = 'JUV'

# Dictionary to convert the stype "codes" (above) into the "stype" values used in Babase
stypesBabase = {}
stypesBabase[stypeAdultFem] = 'F'
stypesBabase[stypeJuv] = 'J'

# Focal activity that indicates feeding
focalFeeding = 'F'

# Necessary prefix for any text notes to be recorded in the ALLMISCS table
allMiscsPrefix = 'O, '