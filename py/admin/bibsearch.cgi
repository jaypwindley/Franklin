#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              TAG( bibsearch.cgi )
#  Description:       Web front-end for SRU bibliographic search
#  Author:            Jay Windley <jwindley>
#  Created:           Wed Sep 11 12:36:00 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------

import cgi
import sys

sys.path.append( '../lib' )
import             config
import             SRU
import             spool
from switch import switch
from HTML   import HTML_page

page = HTML_page( 'Franklin :: Bibliographic Search' )

# Submitted search.  Empty search fields are not reported as field
# storage, so convert only the defined search terms into SRU queries.
#
form = cgi.FieldStorage()
query_args = {}
for key in form.keys():
    query_args[ key ] = form[ key ].value

# If the search is non-empty, convert it to an SRU query and run it.
# For now, redirect to the review_downloads page since xml_breakout
# yet has no facility to direct MARC records to other places, nor do
# we yet have a generic promote/delete facility.
#
if len( query_args ) > 0:
    query = SRU.Query( query_args )
    try:
        spool.xml_breakout( xml_data = query.submit() )
        page.redirect( 'review_downloads.cgi?bibsearch.cgi=redirect' )
    except LookupError:
        page.p( 'No records found' )

# Present the search page.
page.p( 'Bibliographic search:' )

page.body.append( '''
   <form method="POST"
         action=bibsearch.cgi
         name="search"
         ''' )

page.p( 'LCCN <input type="text" name="LCCN" />' )
page.p( 'Title <input type="text" name="title" />' )
page.p( 'Author <input type="text" name="author" />' )
page.p( 'ISBN <input type="text" name="ISBN" />' )
page.p( '<input type="submit" name="submit" value="Submit" /> </form>' )

print str( page )
