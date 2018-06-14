#!/usr/bin/env python
"""
# -----------------------------------------------------------------------
#  File:              franklin_rpc_svc.py
#  Description:       Franklin RPC server
#  Author:            Jay Windley <jwindley>
#  Created:           Tue Mar 10 22:07:10 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""

import sys
import BaseHTTPServer
import SocketServer

import JSONRPC2

# Make this configurable
PORT = 1138

#***********************************************************************
#
#  Franklin RPC Handler, essentially an RPC server instance.  The HTTP
#  functions are handled by the super class.  Each subclass registers
#  itself under a URL path to which JSON RPC 2.0 requests should be
#  directed.
#
#***********************************************************************
class Franklin_RPC_Handler( BaseHTTPServer.BaseHTTPRequestHandler ):

    path_handlers = {}
    
    def __init__( self, request, client_address, server ):
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(
            self,
            request,
            client_address,
            server
        )

        
    #-------------------------------------------------------------------
    # Reject all HTTP methods except POST, via HTTP 501 status.
    #
    def do_GET( self ):
        self.send_error( 501 )
        return False;

    def do_PUT( self ):
        self.send_error( 501 )
        return False;

    def do_OPTIONS( self ):
        self.send_error( 501 )
        return False;



    #-------------------------------------------------------------------
    # Handle the HTTP POST.  Extract the HTTP request paylod, decode it
    # as a JSON RPC 2.0 Request, and send it to the handler for the path
    # given in the POST method.
    #
    def do_POST( self ):

        # Get the request length.  Client must send it.
        try: body_len = int( self.headers[ 'content-length' ] )
        except KeyError, TypeError:
            self.send_error( 411 )
            return False

        # Read the request body.
        body = self.rfile.read( body_len )

        # Parse and validate it.
        try:
            requests = JSONRPC2.decode( body )
        except JSONRPC2.Bad_Request as e:
            err = JSONRPC2_Response( e.id )
            err.error( e.code, e.message )
            content = str( err )

        # Dereference the path handler and tell it to dispatch the JSON
        # RPC 2.0 request to its internal methods.
        #
        if isinstance( requests, list ):
            # XXX don't handle lists yet.
            responses = []
        else:
            responses = self.path_handlers[ self.path ].dispatch( requests )

        # Convert the response to a JSON RPC 2.0 Response.
        content = str( responses )

        # Write the Response back to the client.
        self.send_response( 200 )
        self.send_header( 'Content-Type', 'application/json' )
        self.end_headers()

        self.wfile.write( content )
        return True
    



# XXX move this to a "real" main program.


hdlr = Franklin_RPC_Handler

# Add the Bibliographic RPC handler.
import bib_rpc_svc
Franklin_RPC_Handler.path_handlers[ '/bib' ] = bib_rpc_svc.Handler_Bib( '/bib' )

#import staff_rpc_svc
#Franklin_RPC_Handler.path_handlers[ '/staff' ] = staff_rpc_svc.Handler_Staff( '/staff' )

# Set HTTP server options.
SocketServer.TCPServer.allow_reuse_address = True;
rpcd = SocketServer.TCPServer( ("", PORT), hdlr)
rpcd.protocol_version = 'HTTP/1.0'

try:
    rpcd.serve_forever()
except KeyboardInterrupt:
    print
    sys.exit( 0 )
