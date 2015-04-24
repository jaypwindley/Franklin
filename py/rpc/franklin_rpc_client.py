#!/usr/bin/env python
"""
# -----------------------------------------------------------------------
#  File:              franklin_rpc_client.py
#  Description:       Franklin RPC client
#  Author:            Jay Windley <jwindley>
#  Created:           Wed Apr 15 23:30:10 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""

import httplib
import inspect
import JSONRPC2




#***********************************************************************
#
#  Exceptions raised by client-side calls that translate to RPC calls.
#
#     module       Franklin RPC module that serves the request,
#                  expressed as the HTTP URL path that maps to a
#                  specific module.
#
#     func         The RPC-mappable client-side function that raised
#                  the exception.
#
#     code         The error code from the RPC response.
#
#     message      The error message from RPC response.
#
#     data         Supporting data, if any, from the RPC response.
#
#  This supposes there's no use pretending the RPC mechanism is not
#  using JSON RPC 2.0 under the hood.
#
#***********************************************************************
class RPC_Error( Exception ):
    """Error raised by Franklin RPC clients"""
    
    def __init__( self, client, response ):
        try: self.module  = getattr( client, 'URL' )
        except KeyError: self.module  = '???'
        self.func    = inspect.stack()[1][3]
        self.code    = response.error[ 'code'    ]
        self.message = response.error[ 'message' ]
        self.data    = response.error[ 'data'    ]
        
    def __str__( self ):
        return 'RPC error {module}::{func}::{code} {message} ({data})'.format(
            module  = self.module,
            func    = self.func,
            code    = self.code,
            message = self.message,
            data    = str( self.data ) )


#***********************************************************************
#
#  Base class for all RPC clients.
#
#***********************************************************************
class Franklin_RPC_Client( object ):
    """Base-class client for Franklin RPC services.  Clients for specific
    Franklin modules should subclass this.

    """

    def __init__( self, remote_host, port ):
        self.remote_host = remote_host
        self.port = port

    def __str__( self ):
        try: URL = getattr( self, 'URL' )
        except KeyError: URL = ''
        return 'jsonrpc2://{host}:{port}{url}'.format(
            host = self.remote_host,
            port = self.port,
            url = URL )


    #-------------------------------------------------------------------
    # Send the JSON request to URL at the remote_post and port.  Return
    # the resulting JSON response, which may be an error response.
    # Subclasses are responsible for determining what to do with an
    # error.  May also raise Bad_Request exceptions for transport or
    # protocol level errors with JSON or HTTP.
    #
    def send( self, URL, JSON_request ):
        """Send a JSON request to URL at the server.  Return a JSON_Response.

        """
        cxn = httplib.HTTPConnection( self.remote_host, self.port )
        cxn.connect()
        cxn.request( 'POST', URL, str( JSON_request ) )
        HTTP_response = cxn.getresponse()

        # Server should return HTTP 200 even if the JSON request itself
        # met an error.  If the server returns something other that 200,
        # then it's a server-side error.
        #
        if HTTP_response.status != 200:
            return Bad_Request(
                -32603,
                id = JSON_request.id,
                message = 'HTTP {}'.format( HTTP_response.status ) )
        else:
            JSON_response = HTTP_response.read()
            return JSONRPC2.Response( 0, data = JSON_response )





        
        
if __name__ == '__main__':
    c = Franklin_RPC_Client( 'localhost', 1138 )
    r = JSONRPC2.Request( 'test', arg1 = 'value1', arg2 = 42 )
    print c.send( '/bib', r ).result

