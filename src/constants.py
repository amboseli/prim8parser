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

# Special values from Babase for behaviors
bb_agonism_A = 'AS'
bb_agonism_D = 'DS'
bb_agonism_O = 'OS'
bb_groom = 'G'
bb_mount = 'M'
bb_ejaculation = 'E'
bb_consort = 'C'

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
prim8Version = '1.151128'
prim8Setup = 'DEC15' # Used to populate the "setupid" in babase. The name "setup" made more sense for Psion data. It makes less sense for Prim8.

# Dictionary with abbreviations for all the tablets in use and their descriptions in Babase (SAMPLES_COLLECTION_SYSTEMS.Descr)
collection_systems = {}
collection_systems['SA'] = 'Samsung Tablet A'
collection_systems['SB'] = 'Samsung Tablet B'
collection_systems['SC'] = 'Samsung Tablet C'
collection_systems['SD'] = 'Samsung Tablet D'
collection_systems['SE'] = 'Samsung Tablet E'
collection_systems['SF'] = 'Samsung Tablet F'
collection_systems['SG'] = 'Samsung Tablet G'
collection_systems['SH'] = 'Samsung Tablet H'
collection_systems['SI'] = 'Samsung Tablet I'

# Used when compiling agonisms
agonismCodes = [bb_agonism_A, bb_agonism_D, bb_agonism_O]

# Neighbor codes used in Prim8, and their Babase counterparts
p8_nghcodes = ['N0', 'N1', 'N2']

neighborsFem = {}
neighborsFem[p8_nghcodes[0]] = '1'
neighborsFem[p8_nghcodes[1]] = 'A'
neighborsFem[p8_nghcodes[2]] = 'O'

neighborsJuv = {}
neighborsJuv[p8_nghcodes[0]] = '1'
neighborsJuv[p8_nghcodes[1]] = '2'
neighborsJuv[p8_nghcodes[2]] = '3'

# "Unknown" snames used in Prim8, and their Babase counterparts
unknSnames = {}
unknSnames['996'] = '996'
unknSnames['997'] = '997'
unknSnames['998'] = '998'
unknSnames['NULL'] = 'NULL'
unknSnames['XXX'] = 'NULL'

# Codes used in Prim8 when sname was not known at the time.
# Any incidence of these will need to be corrected before upload to Babase.
immigrantCode = 'IMM' #For new, not-yet-named immigrant males
infantCode = 'INF' #For new, not-yet-named infants
unnamedCodes = [immigrantCode, infantCode]

# Codes representing focal sample "types" (adult females vs. juveniles)
stypeAdultFem = 'FEM'
stypeJuv = 'JUV'
stypeOther = 'OTHER'

# Dictionary to convert the stype "codes" (above) into the "stype" values used
# in Babase. The "other" type is not used in Babase and only occurs if something
# went wrong, so it's not added here.
stypesBabase = {}
stypesBabase[stypeAdultFem] = 'F'
stypesBabase[stypeJuv] = 'G' # As of 16 Sep 2024, this type changed to "Generic"

# Focal activity that indicates feeding
focalFeeding = 'F'

# Focal things implying infant presence/absence
# In adult female PNT rows, the act/behavior is 4 alphanumeric characters. The
# last two of those indicate something about the focal female's infant, if she
# has one. If she doesn't have an infant at the time, then the first of those
# two characters should be:
pntActNoInfant = 'N'

# Maximum number of points in a focal sample.  If more than this,
# then problem.
maxPointsPerFocal = 10

# Prefixes for text to be recorded in the ALLMISCS table
#   This is clunky, an artifact of how these data used to be recorded.  See
#   Babase documentation of the ALLMISCS table for more info.
allMiscsPrefixConsort = 'C'
allMiscsPrefixOther = 'O'

# Behaviors recorded as adlibs that we want saved only as notes, not adlibs
saveAsNotes = [bb_mount, bb_ejaculation, bb_consort]

# Divider for output text files, to divide up sections
textBoundary = '-----------------------------------------------------------------------\n'

# Long names for behaviors
# Useful when checking for behavior notes in free-form text.
# E.g. sometimes a note will be "AAA consort BBB" and not "AAA C BBB"
bb_mount_long = 'mount'
bb_ejaculation_long = 'ejaculate' #Pretty sure no one bothers to spell this out
bb_consort_long = 'consort'
bb_consort_long2 = 'consorting'

# File header for gathered data from files w/ different headers.
# e.g. different tablets, different Prim8 version, etc.
multiFileHeader = 'Data combined from files with different headers\n'
