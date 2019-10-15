#!/usr/bin/env python3

import sys
sys.path.append( '..' )
import api_tools

from flask import Blueprint

responder = Blueprint( 'auth', __name__ )


@responder.route( '/auth/login', methods = [ 'GET' ] )
@api_tools.to_json
@api_tools.errno
def login():
    """Validate user name and password"""
    return { 'user' : 'foo', 'token' : 'foo' }


@responder.route( '/auth/tokens', methods = [ 'GET' ] )
@api_tools.to_json
@api_tools.errno
def tokens():
    """Get list of active tokens"""
    return { 'tokens' : [] }


@responder.route( '/auth/token/<t>', methods = [ 'GET', 'DELETE' ] )
@api_tools.to_json
@api_tools.errno
def show_or_edit_token():
    return { 'token' : t }
