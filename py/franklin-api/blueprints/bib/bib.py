#!/usr/bin/env python3

import sys
sys.path.append( '..' )
import api_tools as API

from flask import Blueprint

responder = Blueprint( 'bib', __name__ )


@responder.route( API.route( '/bib/id' ), methods = [ 'DELETE', 'GET', 'POST', 'PUT', 'PATCH' ] )
def handle_ID():
    return "MARC record"
