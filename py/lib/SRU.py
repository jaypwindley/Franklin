#!/usr/bin/env python
"""
# -----------------------------------------------------------------------
#  File:              TAG( SRU.py )
#  Description:       SRU query for bibliographic entry
#  Author:            Jay Windley <jwindley>
#  Created:           Tue Sep 24 13:27:30 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""

import re
import urllib
import httplib

import config

#***********************************************************************
#
#  SRU bibliographic query.
#
#     Wraps a URL for LoC SRU (Search/Retrieve via URL) query.
#     Construct the object, set additional terms using
#     Query.set_terms(), adjust the Boolean junction (AND or OR) with
#     Query.junction, and run the query via Query.submit().
#
class Query( object ):

    # SRU keys mapped from built-in keys.  Pass a dictionary with the
    # left-hand-side labels as (logical) keys and the values as search
    # arguments.  Can be passed as <args> to constructor or set
    # subsequently using set_terms().
    #
    query_keys = {
        'title'    : 'dc.title',
        'author'   : 'dc.author',
        'LCCN'     : 'bath.lccn',
        'ISBN'     : 'bath.isbn',
        'ISSN'     : 'bath.issn',
        'key'      : 'bath.any'
        }

    #-------------------------------------------------------------------
    # Initialize the members with the config defaults.  If args is
    # given as a dictionary, add the terms.
    #
    def __init__( self, args = None ):
        self.host     = config.SRU['host']
        self.port     = config.SRU['port']
        self.path     = config.SRU['path']
        self.op       = config.SRU['search']['op']
        self.version  = config.SRU['version']
        self.max_recs = config.SRU['search']['max_recs']
        self.schema   = config.SRU['search']['schema']
        self.timeout  = config.SRU['timeout']
        self.junction = ' AND '
        self.set_terms()               # define all the keys...
        self.set_terms( args )         # ...then selectively set them.


    #-------------------------------------------------------------------
    # Set the search terms.  Whatever keys are set in <args> are
    # written into the built-in search terms.  If args is None, the
    # search terms are reset.
    #
    def set_terms( self, args = None ):
        if args is None:
            self.terms = {
                'title'  : None,
                'author' : None,
                'LCCN'   : None,
                'ISBN'   : None,
                'ISSN'   : None,
                'key'    : None
                }
        else:
            for k in args.keys():
                self.terms[ k ] = args[ k ]


    #-------------------------------------------------------------------
    # Encode the object properties as an SRU encoded CGI argument
    # string.
    #
    def CGI_args( self ):
        """URL-encode the SRU request properties"""
        CGI = {
            'operation'      : self.op,
            'version'        : self.version,
            'recordSchema'   : self.schema,
            'maximumRecords' : self.max_recs,
            'query'          : self.terms_str()
            }
        return urllib.urlencode( CGI )


    #-------------------------------------------------------------------
    # Add up all the defined search terms into a CGI substring.
    #
    def terms_str( self ):
        strs = []
        for k in self.terms.keys():

            # Omit if the term isn't defined, or if it isn't one of
            # the defined search keys.
            #
            try:
                if self.terms[ k ] is None: continue
                if self.query_keys[ k ] is None: continue
            except KeyError:
                continue

            # Encode name-value pairs using the SRU domain-attribute
            # keys and the given values.
            #
            self.terms['LCCN'] = normalize_LCCN( self.terms['LCCN'] )
            self.terms['ISBN'] = normalize_ISxN( self.terms['ISBN'] )
            self.terms['ISSN'] = normalize_ISxN( self.terms['ISSN'] )
            strs.append( '{}={}'.format( self.query_keys[ k ],
                                         self.terms[ k ] ) )
        return self.junction.join( strs )

    #-------------------------------------------------------------------
    # Submit the embodied query and return the result.
    #
    def submit( self ):
        """Submit an SRU request and return its answer"""
        conn = httplib.HTTPConnection( host    = self.host,
                                       port    = self.port,
                                       timeout = self.timeout )
        conn.request( 'GET', '{}?{}'.format( self.path, self.CGI_args() ) )
        answer = conn.getresponse()
        if answer.status is not 200:
            raise LookupError
        data = answer.read()
        conn.close()
        return data
                      

    #-------------------------------------------------------------------
    # Return the query as a full URL with CGI arguments properly
    # encoded.
    #
    def __str__( self ):
        return 'http://{host}:{port}{path}?{args}'.format(
            host = self.host,
            port = self.port,
            path = self.path,
            args = self.CGI_args()
            )    


'''
From http://www.loc.gov/z3950/lcserver.html

Number searches (ISBN, ISSN, LCCN, etc.):
       Use a hyphen in all ISSN search terms (e.g., 1234-5678).
       Do not include hyphens in ISBN or LCCN search terms.
       LCCN search terms should be in normalized format (i.e., include
           any prefix, spaces, or zero fill).  For example, LCCN 91-13
           should be "91000013" in the search term.  
'''

#-----------------------------------------------------------------------
# Return the Bath-canonical ISBN/ISSN for the given loosely-specified
# ISBN/ISSN.
#
#   - Remove internal punctuation
#   - Recognize and pass EAN-13 formats
#   - Pad with leading zeros to 10 digits if needed
#
def normalize_ISxN( num ):
    """Normalize an ISBN or ISSN"""
    if num is None: return None
    num = num.replace( '-', '' )
    if re.match( r'^978', num ) is not None:
        return num
    if len( num ) < 10:
        return "%010s" % { num }
    return num


#-----------------------------------------------------------------------
# Return the Bath-canonical LCCN for the given loosely-specified LCCN.
# Canonical form is 8 digits
#
#    YYSSSSSS
#
# where YY means the year, which appears before the dash '-', and the
# remainder SSSSSS is the zero-padded serial number of the catalog
# number.
#
def normalize_LCCN( LCCN ):
    """Normalize a LCCN"""
    if LCCN is None: return None
    parts = LCCN.split( '-' )
    if len( parts ) == 1:
        if len( parts[ 0 ] ) == 8:
            return LCCN               # already canonical form
        else:
            year   = int( LCCN[:2] )  # assume dash-less entry 
            serial = int( LCCN[2:] )
    else:
        year   = int( parts[ 0 ] )
        serial = int( parts[ 1 ] )

    return '%02d%06d' % ( year, serial )
    
