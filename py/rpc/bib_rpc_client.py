#!/usr/bin/env python
"""
# -----------------------------------------------------------------------
#  File:              bib_rpc_client.py
#  Description:       Franklin Bibliographic RPC client
#  Author:            Jay Windley <jwindley>
#  Created:           Wed Apr 15 23:31:53 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""
import sys
sys.path.append( '../lib' )

import  config
from    MARC_bib             import MARC_bib
from    franklin_rpc_client  import Franklin_RPC_Client, RPC_Error
import  JSONRPC2


#***********************************************************************
#
#  RPC client for the Bibliographic module.
#
#***********************************************************************
class Bib_RPC_Client( Franklin_RPC_Client ):
    """Client to the Franklin Bibliographic RPC server."""

    def __init__( self,
                  remote_host = config.RPC[ 'bib' ][ 'host' ],
                  port = config.RPC[ 'bib' ][ 'port' ] ):
        super( Bib_RPC_Client, self ).__init__( remote_host, port )
        self.URL = '/bib'

        
    #-------------------------------------------------------------------
    # Search for keywords.  Returns an iterable of tuples representing
    # the keyword matches.  tuple[ 0 ] is the control number of a
    # matching bibliographic record.  tuple[ 1 ] is the count of the
    # strength of the match.  The iterable is sorted in decreasing order
    # of the match strength.
    #
    #   key_list:               list of keywords to match.
    #
    #   domeain_list:           list of keyword domains to match, any
    #                           of 'T' (title), 'A' (author), or 'S'
    #                           (subject).  May be omitted or empty, in
    #                           which case all domains are searched.
    #
    #   limit:                  maximum number of matches to return.
    #                           May be omitted or zero, in which case
    #                           all matches are returned.
    #
    def search( self, key_list, domain_list = [], limit = 0 ):
        """Search for keywords from key_list having record types in domain_list.

        """
        err = JSONRPC2.Response( 0 )

        # Be generous.  If a single string is given as the keyword,
        # listify it.
        #
        if isinstance( key_list, str ):
            key_list = [ key_list ]
        if len( key_list ) == 0:
            err.set_error( -32602, data = "key_list is empty" )
            raise RPC_Error( self, err )
        
        params = { 'keys' : key_list }
        if limit > 0:
            params[ 'limit' ] = limit
        if len( domain_list ) > 0 and isinstance( domain_list, list ):
            params[ 'domain' ] = domain_list
        response = self.send(
            self.URL,
            JSONRPC2.Request( 'search', **params ) )
        if not response: raise RPC_Error( self, response )
        return [ tuple( row ) for row in response.result ]
    



    
    #-------------------------------------------------------------------
    # Retrieve the bibliographic records having the given control
    # numbers.  Returns a dict whose keys are input control numbers and
    # the values are either MARC21 records or None if the record was not
    # found.
    #
    #   ctl_nums...:            list of control numbers of bibliographic
    #                           records to retrieve, or a single control
    #                           number.
    #
    def get( self, *ctl_nums ):
        """Retrieve bibliographic records having the given control number(s).

        """
        response = self.send(
            self.URL,
            JSONRPC2.Request( 'get', *ctl_nums ) )
        if not response: raise RPC_Error( self, response )

        # Convert all the text representations to MARC_bib records.
        for k in response.result:
            if response.result[ k ] is not None:
                response.result[ k ] = MARC_bib( data = response.result[ k ] )
        return response.result


    

    #-------------------------------------------------------------------
    # Retrieve for editing a bibliographic record having the given
    # control number, along with its base checksum that must be
    # submitted to the subsequent store() call.
    #
    #   session_key:            A valid session key containing the
    #                           appropriate rights.
    #
    #   ctl_num:                The control number of the bibliographic
    #                           record to retrieve for editing.
    #
    def edit( self, session_key, ctl_num ):
        """Retrieve the bibliographic record having the given control number,
        for editing, with checksum.

        """
        response = self.send(
            self.URL,
            JSONRPC2.Request(
                'edit',
                session = session_key,
                ctl_num = ctl_num ) )
        if not response: raise RPC_Error( self, response )

        # Convert the bibliographic record to MARC_bib object.
        response.result[ 'record' ] = MARC_bib(
            data = response.result[ 'record' ]
        )
        return response.result
    


    
    #-------------------------------------------------------------------
    # Store the given bibliographic record.  If the record already
    # exists, replace it with the given one so long as the checksum
    # matches the existing record.  If the record is new, checksum is
    # ignored.
    #
    #   session_key:            A valid session key containing the
    #                           appropriate rights.
    #
    #   record:                 MARC_bib object to be stored.
    #
    #   checksum:               The checksum produced by the edit() call
    #                           when the submitted record was retrieved
    #                           for editing.  Required only for edited
    #                           records, not new records.
    #
    def store( self, session_key, record, checksum = '' ):
        """Store the bibliographic record.  Verify with checksum and session
        key.

        """
        response = self.send(
            self.URL,
            JSONRPC2.Request(
                'store',
                session = session_key,
                record = str( record ),
                checksum = checksum ) )
        if not response: raise RPC_Error( self, response )
        return response.result


    
    #-------------------------------------------------------------------
    # Delete the bibliographic record having the given control number.
    #
    #   session_key:            A valid session key containing the
    #                           appropriate rights.
    #
    #   ctl_num:                The control number of the bibliographic
    #                           record to delete
    #
    def delete( self, session_key, ctl_num ):
        """Delete the bibliographic record.

        """
        reponse = self.send(
            self.URL,
            JSONRPC2.Request(
                'delete',
                session = session_key,
                ctl_num = ctl_num ) )
        if not response: raise RPC_Error( self, response )


    def LC_search( self, search_type, value ):
        """Search the Library of Congress catalog

        """
        response = self.send(
            self.URL,
            JSONRPC2.Request(
                'LC_search',
                search_type = search_type,
                value = value ) )
        if not response: raise RPC_Error( self, response )
        response.result = map( str, response.result )
        return response.result





    
if __name__ == "__main__":
    c = Bib_RPC_Client( 'localhost', 1138 )
    # print c.search( [] )
    # try: print c.search( ['audi'] )
    # except RPC_Error as e: print e
    # try: print c.search( 'dinner' )
    # except RPC_Error as e: print e    
    # try: print c.search( [ 'watercolor' ], limit = 'limit' )
    # except RPC_Error as e: print e
    # try: print c.search( [ 'watercolor' ], domain_list = ['A'] )
    # except RPC_Error as e: print e
    # print c.get( 'BTCTA16227491' )[ 'BTCTA16227491' ]
    # print c.get( 'DLC3054826', 'BTCTA16227491' )
    print c.LC_search( 'title', 'lorax' )
    #r = c.edit( ctl_num = 'BTCTA16227491', session_key = '' )
    #print c.store( session_key = 0, record = r[ 'record' ], checksum = '0' )
    #print "get", c.get( 'BTCTA16227491' )[ 'BTCTA16227491' ]
