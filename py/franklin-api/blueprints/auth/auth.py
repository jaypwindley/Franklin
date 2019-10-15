#!/usr/bin/env python3

import sys
sys.path.append( '..' )
import api_tools as API

from flask import Blueprint

responder = Blueprint( 'auth', __name__ )


@responder.route( API.route( 'auth/login' ), methods = [ 'GET' ] )
@API.to_json
@API.errno
def login():
    """Validate user name and password"""
    return { 'user' : 'foo', 'token' : 'foo' }


@responder.route( API.route( 'auth/tokens' ), methods = [ 'GET' ] )
@API.to_json
@API.errno
def tokens():
    """Get list of active tokens"""
    return { 'tokens' : [] }


@responder.route( API.route( 'auth/token/<t>' ), methods = [ 'GET', 'DELETE' ] )
@API.to_json
@API.errno
def show_or_edit_token( t ):
    return { 'token' : t }
