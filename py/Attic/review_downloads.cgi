#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              TAG( review_downloads.cgi )
#  Description:       Promote or discard scans and downloads
#  Author:            Jay Windley <jwindley>
#  Created:           Thu May  2 13:00:41 20
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------

import cgi
import sys
import time
from   os        import listdir, unlink, chdir
from   os.path   import isfile, join, getctime

sys.path.append( '../lib' )
import                config
import                spool
from switch    import switch
from HTML      import HTML_page
from MARC      import MARC_record
from MARC_HTML import MARC_HTML_renderer

# Go find the spool directory.
chdir( config.PATHS['spool']['MARC'] )

destination = '/franklin/admin/review_downloads.cgi'

# Start the HTML response, in case there needs to be a web-reported
# error message.
#
page = HTML_page( title = 'Franklin Admin :: Review Bibliographic Scans' )
renderer = MARC_HTML_renderer()

# Get the POST values and do something with them.
form = cgi.FieldStorage()
for path in form.keys():

    for case in switch( form[ path ].value ):

#        if case( 'redirect' ):
#            destination = form[ path ].value
#            break
        
        if case( 'defer' ):
            break

        # Move the MARC record to the upload directory.
        if case( 'promote' ):
            if config.DEBUG: page.p( '{} promoted'.format( path ) )
            try:
                spool.db_upload( path )
                unlink( path )
            except spool.SQLError as e:
                page.p( '<b>{}</b>'.format( str( e ) ) )
            except spool.DuplicateEntry as e:
                if config.DEBUG:
                    page.p( 'Duplicate entry {}'.format( str( e ) ) )
                unlink( path )
            break

        # Delete the MARC record.
        if case( 'remove' ):
            if config.DEBUG: page.p( '{} removed'.format( path ) )
            unlink( path )
            break;

        if case():
            break
        

# Get the files that remain.
files = [ f for f in listdir( '.' ) if isfile( f ) ]

# Regardless of whether there are any downloads, there will be a form.
#
page.body.append( """
                  <form method="POST"
                        action="{}"
                        name="selection">
                   """.format( destination )
                  )

if len( files ) == 0:
    page.p( 'No downloads found.')
    submit_name = 'Rescan'
    
else:

    submit_name = 'Submit'
    
    for path in files:

        f = open( path, 'r' )
        rec = MARC_record( data = f.read() )
        f.close()

        # Show the citation.
        page.body.append( renderer.render( rec, spacer = ' &mdash; ' ) )

        # Radio buttons for the final disposition of the file.
        page.p( """
            <input type="radio" name="{}" value="defer" checked="true"> Defer </input>
            <input type="radio" name="{}" value="remove"> Remove </input>
            <input type="radio" name="{}" value="promote"> Promote </input>
            """.format( path, path, path )
                )

        # Search time and file name.
        page.body.append( """
            <div align=right><font size=-1 color="#888888">{} {}</font></div>
                      """.format( path, time.ctime( getctime( path ) ) ) )
        page.hr()

page.p( '<input type="submit" value="{}" /> </form>'.
        format( submit_name ) )

print str( page )
