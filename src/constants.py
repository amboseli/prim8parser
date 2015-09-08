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
proxBehavName = 'proximity'


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

# The current Prim8 version #
prim8Version = '1.150510'

# Used when compiling agonisms
agonismCodes = ['AS', 'OS', 'DS']