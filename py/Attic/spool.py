#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              TAG( spool.py )
#  Description:       MARC/XML spool operations
#  Author:            Jay Windley <jwindley>
#  Created:           Tue Sep 10 13:37:26 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------

import os
import sys
import config

from   MARC        import MARC_record
from   data_bib    import data_bib
import MySQLdb     as     mdb
from   MARC_XML    import MARC_XML_parser
from   MARC_Z392   import MARC_Z392_renderer



#-----------------------------------------------------------------------
# Read the fully-qualified path name xml_path and determine whether it
# contains any encoded MARC records.  If so, break them out into
# individual MARC files in the standard spool.  Raises LookupError if
# the XML file is invalid or contains zero records (a popular result
# when LoC lookups fail).
#
def xml_breakout( xml_path = None, xml_data = None ):
    XML = MARC_XML_parser()

    # See how many records were returned.
    #
    #  XXX This is a stupid way to receive the arguments.  Granted
    #      sometimes we read from a file and other times from in-core
    #      data, but this is an orthogonality nightmare.
    #
    if xml_path is not None:
        XML_tree = XML.parse_file( xml_path )
    elif xml_data is not None:
        XML_tree = XML.parse_string( xml_data )
    if len( XML_tree ) == 0:
        raise LookupError

    # For logging the incoming records.  Essentially we never throw
    # away anything, but we do store it in a more concise format.
    #
    Z392 = MARC_Z392_renderer()
    z392_log = open( config.PATHS['data'] + 'log', 'a' )

    # Break out the MARC records from the XML file for review.
    #
    for rec in XML_tree:

        # Log the raw record, if possible.
        try:
            z392_log.write( Z392.render( rec ).encode( 'ascii',
                                                       errors = 'ignore' ) )
        except ValueError:
            pass

        # Remove 9XX tags.  They are LOC local data that we don't care
        # about.
        #
        rec.tags = [ t for t in rec.tags if t.tag[:1] != '9' ]

        # Write the canonical record to its own file.
        #
        marc_out = open( config.PATHS['spool']['MARC'] + rec.ctl_num(), 'w' )
        marc_out.write( str( rec ) );
        marc_out.close()

    z392_log.close()

#-----------------------------------------------------------------------
# Error in (generated) SQL code.
#
# XXX should be part of data_mysql.py
#
class SQLError( BaseException ):       pass

#-----------------------------------------------------------------------
# Attempt to upload a record with a control number that is already
# defined.  Stringifies to the conflicting control number.
#
class DuplicateEntry( BaseException ): pass


#-----------------------------------------------------------------------
# Read the fully-qualified file at <path> as a canonical MARC record
# and attempt to upload it to the bibliographic database.
#
# Can raise SQLError or DuplicateEntry.
#
def db_upload( path ):

    # Connect to the database.
    db = data_bib( { 'user': config.CREDENTIALS['database']['bib']['user'],
                     'pass': config.CREDENTIALS['database']['bib']['pass'],
                     'host': config.CREDENTIALS['database']['bib']['host'] } )

    # Read the MARC record.
    f = open( path, "r" )
    rec = MARC_record( f.read() )

    try:
        db.add( rec )
    except mdb.IntegrityError as e:
        raise DuplicateEntry( str( e ) + os.path.basename( path ) )
    except mdb.ProgrammingError as e:
        raise SQLError( 'SQL error: {}'.format( e ) )

