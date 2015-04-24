#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              TAG( xml_breakout.py )
#  Description:       Split MARCXML files into individual MARC files
#  Author:            Jay Windley <jwindley>
#  Created:           Wed Jul 17 16:47:47 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------

import os
import sys
import getopt

sys.path.append( '../lib' )
import                  config
from switch      import switch
from MARC_XML    import MARC_XML_parser
from MARC_Z392   import MARC_Z392_renderer

delete_xml = False

# Get command line options.
#
#  --arch        where the archive directory lives, for logs.
#                See above for default.
#  --del         delete XML files after they've been split.
#                Default is no.
#  --marc-dir    where to write the split_out MARC files.
#                See above for default.
#
try:
    opts, args = getopt.getopt( sys.argv[1:],
                                "m:da:",
                                [ "marc-dir=", "del", "arch=" ] )
except getopt.GetoptError as err:
    print str( err )
    sys.exit( 1 )

for opt in opts:
    for case in switch( opt[0] ):
        if case( '-d' ) or case( '--del' ):
            delete_xml = True
            break
        if case( '-m' ) or case( '--marc-dir' ):
            marc_dir = opt[1]
            break;
        if case( '-a' ) or case( '--arch' ):
            arch_dir = opt[1]
            break;


for arg in args:
    spool.xml_breakout( arg )
    if delete_xml:
        os.remove( arg )

sys.exit( 0 )
