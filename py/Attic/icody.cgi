#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              TAG( icody.py )
#  Description:       Receive an ISBN from iCody and search it
#  Author:            Jay Windley <jwindley>
#  Created:           Thu Aug 22 15:12:35 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------

import cgi
import os
import re
import stat
import subprocess
import sys

sys.path.append( '../lib' )

import config
import spool
import SRU

log_path = config.PATHS['log']['bib']
MARC_path = config.PATHS['spool']['MARC']

#-----------------------------------------------------------------------
# Return <msg> esconced in a suitable plist for display on the mobile
# device.
#
def plist_error( msg ):
    return """
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>type</key>
        <string>alert</string>
        <key>title</key>
        <string>LOC Lookup Failure</string>
        <key>message</key>
        <string>{msg}</string>
    </dict>
    </plist>
    """.format( msg = msg )
    


#-----------------------------------------------------------------------
# Write a message as a plist to the remote device, write a similar
# message to the error log, and then exit non-nicely.  Does not
# return.
#
def bail( msg ):
    print plist_error( msg )
    log.write( 'ERROR: {}\n'.format( msg ) )
    sys.exit( 1 ) 


########################################################################
#                                                                      #
#                              MAIN                                    #

# Prepare to talk back to the scanner device.
#
print 'Content-Type: application/x-plist'

# Open the one-time log and try to make it world-readable
#
log = open( log_path, 'w' )
if log is None:
    print plist_error( 'cannot open log file' )
    exit( 0 )
try: os.chmod( log_path, 0666 )
except OSError: pass


# Get POST values.  If the DEBUG config variable is set, put some
# dummy information in, because it's being run from the command line
# for testing purposes.
#
form = cgi.FieldStorage()
try:
    isbn = form[ 'value' ].value

except KeyError:
    if config.DEBUG:
        isbn = '0891300511'   # valid, but uninteresting.
    else:
        bail( 'POST did not contain scan value' )
        
log.write( 'value = {}\n'.format( isbn ) )

query = SRU.Query( { 'ISBN' : isbn } )

# Break out the individual MARC records from the XML data and move
# them as canonical MARC records to the MARC spool.
#
try:
    spool.xml_breakout( xml_data = query.submit() )
except LookupError:
    bail( 'LOC query return no results for {}'.format( isbn ) )


# Tell the remote device to go Ping!
#
print """
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>type</key>
        <string>sound</string>
        <key>name</key>
        <string>playSuccessSound</string>
    </dict>
    </plist>
    """

log.close()
exit( 0 )
