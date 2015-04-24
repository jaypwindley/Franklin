#!/usr/bin/env python
"""
# -----------------------------------------------------------------------
#  File:              JSONRPC2.py
#  Description:       JSON RPC 2.0 entities
#  Author:            Jay Windley <jwindley>
#  Created:           Fri Apr 17 19:41:35 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""

import json


ENOPARSE   = '-32700'
EINVAL     = '-32600'
ENOTSUP    = '-32601'
EPARM      = '-32602'
EINTERNAL  = '-32603'

#***********************************************************************
#
#  Exception for JSON RPC 2.0 internal errors.  Incorporates the Error
#  abstraction from the standards document.  When this abstraction is
#  raised on the server side, it is usually meant to be caught and
#  translated to an error Response object.
#
#***********************************************************************
class Exception( Exception ):
    """Exception for JSON requests."""

    std_msgs = {
        ENOPARSE  : 'JSON Parse error',
        EINVAL    : 'Invalid JSON RPC Request',
        ENOTSUP   : 'RPC Method not found',
        EPARM     : 'Invalid RPC params',
        EINTERNAL : 'Internal error'
 	}

    def __init__( self, code, id = 'null', message = '', data = {} ):
        
        self.code = code
        self.id   = id
        self.data = data
        
        if message == '':
            try: message = self.std_msgs[ str( code ) ]
            except KeyError:
                message = 'Unknown error'

        super( Exception, self ).__init__( message )



#***********************************************************************
#
#  JSON RPC 2.0 Request.
#
#***********************************************************************
class Request( object ):
    """JSON RPC 2.0 request object."""

    # Facilitates unique ID nubmers.  The number concatenates id_prefix
    # to id_seq.
    #
    id_prefix = 'FC'
    id_seq = 1
    
    def __init__( self, method, *args, **kwargs ):

        # Assign a relatively unique ID number.
        self.id = '{}{}'.format(
            Request.id_prefix,
            Request.id_seq
        )
        Request.id_seq += 1
        self.method = method

        # Positional and keyword arguments cannot be specified
        # simultaneously.
        #
        if len( args ) > 0 and len( kwargs ) > 0:
            raise Exception( ENOPARSE )

        self.params = []
        if len( kwargs ) > 0:
            self.params = kwargs
        if len( args ) > 0:
            self.params = args
        

    #-------------------------------------------------------------------
    # Length refers to the string representation because the most common
    # use for it is the Content-Length header in the HTTP transaction.
    #
    def __len__( self ):
        return len( self.__str__() )

    def __str__( self ):
        """The JSON representation of the object, suitable for transmission as
        a Request object per section 4 of the standard.

        """
        return json.dumps( {
            'jsonrpc': '2.0',
            'id': self.id,
            'method': self.method,
            'params': self.params
        } )



#***********************************************************************
#
#  JSON RPC 2.0 Response.
#
#***********************************************************************
class Response( object ):
    """JSON RPC 2.0 response object."""

    def __init__( self, id, result = 'OK', data = '' ):
        self.id     = id
        self.error  = None
        self.result = result
        if len( data ) > 0:
            d = json.loads( data )
            self.id = d[ 'id' ]
            try:
                self.result = d[ 'result' ]
            except KeyError:
                try:
                    self.set_error( **d[ 'error' ] )
                except KeyError:
                    raise ValueError( 'malformed JSON RPC 2.0 response' )
                    pass
        

    #-------------------------------------------------------------------
    # Convert the response into an error response.  Remove the response,
    # which is inappropriate for an error.  Add the code, messsage, and
    # (optional) data.
    #
    def set_error( self, code, message = '', data = {} ):
        """Convert the object to an error object."""
        
        self.error = { 'code': code, 'message': message }
        self.result = None
        if len( data ) > 0:
            self.error[ 'data' ] = data

            
    #-------------------------------------------------------------------
    # Booleanism for a response is whether or not it's an error.
    #
    def __nonzero__( self ):
        return ( self.error is None )
    def __bool__( self ): return self.__nonzero__()

            
    def __str__( self ):
        """The JSON representation of the object, suitable for transmission as a
        Response object per section 5 of the standard.

        """
        d = { 'jsonrpc': '2.0', 'id': self.id }
        if self.error is not None:
            d[ 'error' ] = self.error
        else:
            d[ 'result' ] = self.result
        return json.dumps( d )



#***********************************************************************
#
#  JSON RPC 2.0 request handler.  Dispatches a JSON RPC 2.0 request to
#  an appropriate class method, marshalling its arguments as they are
#  presented.  Subclasses operate on the server side and implement
#  RPC_<method> where <method> is the JSON RPC 2.0 method it handles.
#
#***********************************************************************
class Handler( object ):

    #-------------------------------------------------------------------
    # Invoke the subclass method that corresponse to the JSON RPC 2.0
    # request.  The method should accomplish whatever the JSON RPC
    # method was meant to do, and return an appropriate JSON RPC 2.0
    # Response object to indicate the results.  If the JSON RPC 2.0
    # Request has positional arguments, they are passed to the RPC
    # method in *args.  If the JSON RPC 2.0 Request has keyword
    # arguments, they are passed to the RPC method in **kwargs.
    #
    def dispatch( self, request ):
        """Call the object method corresponding to the JSON RPC method and
        return the Response object.

        """        
        args     = None
        kwargs   = None
        id       = request[ 'id' ]
        response = Response( id )

        # Determine whether an object method of the appropriate name
        # exists.
        #
        mangled_method = 'RPC_' + request[ 'method' ]
        if not hasattr( self, mangled_method ):
            response.set_error( ENOTSUP, data = request[ 'method' ] )
            return response
        func = getattr( self, mangled_method )

        # Package the arguments appropriately to the structure
        # represented in the request and call the function.
        #
        try:
            if isinstance( request[ 'params' ], list ):
                args = request[ 'params' ]
                return func( id, *args )
            elif isinstance( request[ 'params' ], dict ):
                kwargs = request[ 'params' ]
                return func( id, **kwargs )
        except KeyError:
            return func( id )


    #-------------------------------------------------------------------
    # Toy RPC response method to test handlers.
    #
    def RPC_test( self, id, *args, **kwargs ):
        return str( JSONRPC2_Response( id ) )


    

#-----------------------------------------------------------------------
# Validate a dict that is meant to represent a JSON RPC 2.0 reequest.
# Required fields are tested.  Optional fields are validated if they are
# present.  Extraneous fields are not considered an error, in the spirit
# of lenient acceptance.
#
def validate( request ):
    """Validate a dict representing a JSON RPC 2 request.
    """

    # First check the ID, since we will report errors using it.
    id = 'null'
    try: id = request[ 'id' ]
    except KeyError:
        raise Exception( id = id, code = EINVAL )

    # JSON RPC version must be exactly '2.0'
    try:        
        if request[ 'jsonrpc' ] != '2.0':
            raise Exception( id = id, code = -32600 )
    except KeyError:
        raise Exception( id = id, code = EINVAL )

    # Only the dispatcher knows whether the method specifies a valid
    # action, so just see if it's a valid string.
    #
    try:
        if request[ 'method' ] == '':
            raise Exception( id = id, code = ENOTSUP )
    except KeyError:
        raise Exception( id = id, code = EINVAL )

    # Parmaters are not technically required.  But if they are
    # specified, they must be a structure, either a list or a dict.
    #
    try:
        params = request[ 'params' ]
        if not isinstance( params, dict ) and not isinstance( params, list ):
            raise Exception( id = id, code = EPARM )
    except KeyError:
        pass




#-----------------------------------------------------------------------
# Decode a JSON RPC 2.0 request string into a corresponding dict, or
# list of dicts in the case of a batched request.
#
def decode( JSON_string ):
    """Decode a JSON RPC request to a corresponding dict or list of dicts.

    """
    try: requests = json.loads( JSON_string )
    except:
        raise Exception( id = 'null', code = -32700 )
    
    if isinstance( requests, list ):
        for r in requests:
            try: validate( r )
            except Exception as e:
                raise e
    else:
        validate( requests )

    return requests










    
if __name__ == '__main__':
    # Test the decode and dispatch functions.
    s = '{"jsonrpc":"2.0", "id":42, "method":"test", "params": {"a":42, "b":6}}'
    r = decode( s )
    validate( r )
    h = JSONRPC2_Handler()
    print h.dispatch( r )

    # Test the request functions.
    r = JSONRPC2_Request( 'test' )
    print str( r ), len( r )
    r = JSONRPC2_Request( 'test', arg1 = 'value1', arg2 = 42 )
    print str( r ), len( r )
    r = JSONRPC2_Request( 'test', 1, 2, 'daddy', 4 )
    print str( r ), len( r )

