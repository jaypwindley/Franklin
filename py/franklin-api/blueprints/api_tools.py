#!/usr/bin/env python3

import functools
import json
from flask import Response

import sys
sys.path.append( '../../lib' )
import config

def route( tail ):
    """Compose the path part of the API URL"""
    return config.API[ 'root' ] + tail;


def to_json( func ):
    """Convert function return value to JSON"""
    @functools.wraps( func )
    def wrapper( *args, **kwargs ):
        return Response( json.dumps( func( *args, **kwargs ) ), mimetype = "application/json" )
    return wrapper;


def errno( func ):
    """Add standard result element"""
    @functools.wraps( func )
    def wrapper( *args, **kwargs ):
        d = {}
        err = 0
        msg = None;
        try:
            d = func( *args, **kwargs )
        except:
            err = 42
            msg = 'Something bad happened'

        d[ 'result' ] = { 'errno' : err, 'msg' : msg }
        return d
    return wrapper
