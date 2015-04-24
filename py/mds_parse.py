#!/usr/bin/env python

import sys
import re
import xml.etree.ElementTree as ET

ns_regex = re.compile( '^(\{[^}]*\})(.*)$' )

def delete_namespace( name ):
    m = ns_regex.match( name )
    return m.group( 2 )

def resolve_URL( URL ):
    URL = URL.replace( 'http://id.loc.gov/authorities/subjects/', '' )
    URL = URL.replace( 'http://id.loc.gov/authorities/names/', '' )
    return URL

parser = ET.iterparse( sys.argv[ 1 ], events = ( 'start', 'end' ) );
parser = iter( parser );
ev, root = parser.next();
for ev, elt in parser:

    tag = delete_namespace( elt.tag )
    
    if ev == 'start':
        if tag == 'Description':
            for k in elt.attrib:
                val = elt.attrib[ k ]
                if delete_namespace( k ) == 'about':
                    this = resolve_URL( val )

    if ev == 'end':
        if tag == 'Description':
            this = ''
        if tag == 'authoritativeLabel':
            print elt.text.encode( 'utf-8', 'ignore' )
    
    root.clear();
    
    
