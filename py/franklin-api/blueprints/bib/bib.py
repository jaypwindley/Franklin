#!/usr/bin/env python3

import sys
sys.path.append( '..' )
import api_tools

from flask import Blueprint

responder = Blueprint( 'bib', __name__ )


@responder.route( '/bib/id' )
def get_bib_record():
    return "MARC record"
