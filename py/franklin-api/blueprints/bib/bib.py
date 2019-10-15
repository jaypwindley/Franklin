#!/usr/bin/env python3

import sys
sys.path.append( '..' )
sys.path.append( '../../lib' )

import api_tools as API
from switch import switch

from flask import Blueprint, request

responder = Blueprint( 'bib', __name__ )

@responder.route( API.route( 'bib/id/<ctl_num>' ), methods = [ 'GET', 'POST', 'PATCH', 'DELETE' ] )
def handle_ID( ctl_num ):
    for case in switch( request.method ):
        if case( 'GET' ):
            return "MARC record\n"
        if case( 'POST' ):
            return "new record\n"
        if case( 'PATCH' ):
            return "edit record\n"
        if case( 'DELETE' ):
            return "delete record\n";
