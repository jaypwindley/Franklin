#!/usr/bin/env python
"""
# -----------------------------------------------------------------------
#  File:              bib_rpc_svc.py
#  Description:       Bibliographic RPC service
#  Author:            Jay Windley <jwindley>
#  Created:           Fri Apr 17 21:46:38 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""

import MySQLdb as mdb

import sys
sys.path.append( '../lib' )
from    MARC_bib   import MARC_bib
import  JSONRPC2
from    data_bib   import data_bib
import  config
import  SRU
from    MARC_XML   import MARC_XML_parser


#***********************************************************************
#
#  RPC Handler for the Bibliographic data store.  Implements the RPC
#  methods for manipulating bibliographic records.
#
#***********************************************************************
class Handler_Bib( JSONRPC2.Handler ):

    def __init__( self, path ):
        super( Handler_Bib, self ).__init__()
        self.path = path
        db_name   = 'Franklin'
        self.db   = data_bib( config.CREDENTIALS['database'][db_name] )


    #-------------------------------------------------------------------
    # Keyword arguments:
    #   domain:          (optional) if present, a list of tokens
    #                    defining search domains, where token is any of
    #                    'T' (title), 'A' (author), or 'S' (subject).
    #                    If not specified, all domains are assumed.
    #                    Values other that these are ignored.
    #
    #   keys:            list of keywords to search for.  Must be
    #                    non-empty.
    #
    #   limit:           (optional) if present, a number indicating
    #                    the maximum number of matches to return.
    #
    # Response:
    #   list of matching records in Base-64 encoded Z392 format.
    #        
    def RPC_search( self, id, *args, **kwargs ):
        """Execute bibliographic search."""

        r = JSONRPC2.Response( id )

        # Validate keywords.
        try: keys = kwargs[ 'keys' ]
        except KeyError:
            r.set_error( JSONRPC2.EPARM,
                         data = 'keys parameter is mandatory' )
            return r
        if not isinstance( keys, list ):
            r.set_error( JSONRPC2.EPARM,
                         data = 'keys must be a list' )
            return r
        if len( keys ) == 0:
            r.set_error( JSONRPC2.EPARM,
                         data = 'keys may not be empty' )
        
        # Dereference the domain and validate it.
        try:               domain = kwargs[ 'domain' ]
        except KeyError:   domain = []
        if not isinstance( domain, list ):
            r.set_error( JSONRPC2.EPARM,
                         data = 'if specified, domain must be a list' )
            return r
        
        # Dereference the limit and validate it.
        try:               limit = kwargs[ 'limit' ]
        except KeyError:   limit = 0
        if not isinstance( limit, int ):
            r.set_error( JSONRPC2.EPARM,
                         data = 'if specified, limit must be a number' )
            return r
        if limit < 0:
            r.set_error( JSONRPC2.EPARM,
                         data = 'if specified, limit cannot be negative' )
            return r
        
        r.result = self.db.match_keywords( keys, domain, limit )
        return r





    #-------------------------------------------------------------------
    # List Arguments:
    #   list of control numbers of records to retrieve.
    #
    # Response:
    #   dictionary whose keys are the control numbers from the request
    #   and whose values are the MARC21 records in ASCII format.
    #   Records that cannot be retrieved have null values for the
    #   control-number key in the response.
    #
    # Error codes:
    #   10001 Database error
    #
    def RPC_get( self, id, *args, **kwargs ):
        """
        Retrieves one or more bibliographic records.
        """
        records = {}
        for ctl_num in args:
            r = self.db.view( ctl_num )
            if r is None:
                records[ ctl_num ] = None
            else:
                records[ ctl_num ] = str( r )
        return JSONRPC2.Response(
            id,
            result = records
        )


    #-------------------------------------------------------------------
    # Keyword arguments:
    #   ctl_num:         control number of record to edit.
    #
    #   session:         session key.
    #
    # Response:
    #   record:          The MARC21 record in Base-64 encoded Z392
    #                    format.
    #
    #   checksum:        Storage checksum to be presented upon any
    #                    eventual store operation.
    #
    # Error codes:
    #   10001 Database error
    #   10002 Session invalid
    #   10301 No such record
    #
    def RPC_edit( self, id, *args, **kwargs ):
        """
        Retrieves a record for editing.
        """
        response = JSONRPC2.Response( id )
        #
        # r = self.db.edit( kwargs[ 'ctl_num' ] )
        #
        r = self.db.view( kwargs[ 'ctl_num' ] )
        if r is None:
            response.set_error( 10301, data = "record not found" )
        else:
            response.result = {
                'record': str( r ),
                'checksum': r.digest()
                }
        return response



    #-------------------------------------------------------------------
    # Keyword arguments:
    #   record:          MARC21 record in ASCII format.
    #
    #   checksum:        (optional) storage checksum for existing
    #                    record, optional for new records.
    #
    #   session:         session key.
    #
    # Response:
    #   the control number of the added or updated record.
    #
    # Error codes:
    #   10001 Database error
    #   10002 Session invalid
    #   10401 Stale checksum
    #
    def RPC_store( self, id, *args, **kwargs ):
        """
        Store a bibliographic record.
        """
        rec = MARC_bib( data = kwargs[ 'record' ] )
        response = JSONRPC2.Response( id, result = rec.ctl_num() )
        
        # Try to save as new.  If the data store reports IntegrityError,
        # the record already exists, so shift to updating the existing
        # record.
        #
        try: self.db.add( rec )
        except mdb.IntegrityError:
            try: self.db.edit_commit( rec, kwargs[ 'checksum' ] )
            except ValueError:
                response.set_error( 10401,
                                    message = 'stale checksum',
                                    data = rec.ctl_num() )
        return response



    #-------------------------------------------------------------------
    # Keyword arguments:
    #   ctl_num:         control number of the record to delete.
    #
    #   session:         session key.
    #
    # Response:
    #   the control number of the deleted record.
    #
    # Error codes:
    #  10001 Database error
    #  10002 Session invalid
    #  10501 Record not found
    #
    def RPC_delete( self, id, *args, **kwargs ):
        """
        Delete a bibliographic record.
        """
        db.delete( kwargs[ 'ctl_num' ] )
        return JSONRPC2.Response( id )


    
    #-------------------------------------------------------------------
    # Keyword arguments:
    #   max_matches:     (optional) Maximum number of matches returned
    #                    by LOC.
    #
    #   search_type:     what kind of information to search for in LOC,
    #                    exactly one of:
    #                      LCCN
    #                      title
    #                      author
    #                      ISBN
    #                      ISSN
    #
    #   value:           search terms or strings
    #
    # Response:
    #   list of matching MARC21 bibliographic records in ASCII format.
    #
    def RPC_LC_search( self, id, *args, **kwargs ):
        """
        Search the Library of Congress catalog
        """
        response = JSONRPC2.Response( id, result = [] )

        # Validate search type.
        try:
            if kwargs[ 'search_type' ] not in ( 'LCCN',
                                                'title',
                                                'author',
                                                'ISBN',
                                                'ISSN' ):
                response.set_error( JSONRPC2.EPARM,
                                    data = 'search_type invalid' )
                return response
        except KeyError:
            response.set_error( JSONRPC2.EPARM,
                                data = 'search_type must be specified' )
            return response
        
        # Submit the query.
        query = SRU.Query( { kwargs[ 'search_type' ] : kwargs[ 'value' ] } )
        try: query.max_recs = kwargs[ 'max_matches' ]
        except KeyError: pass
        XML_data = query.submit()
        parser = MARC_XML_parser()
        rec_list = parser.parse_string( XML_data )
        for r in rec_list:
            print r.ctl_num()
        # response.result = map( str, parser.parse_string( XML_data ) )

        return response
