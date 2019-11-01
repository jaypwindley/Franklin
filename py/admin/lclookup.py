#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              lclookup.py
#  Description:       LC catalog lookup and store
#  Author:            Jay Windley <jwindley>
#  Created:           Fri Oct 11 17:38:34 2019
#  Copyright:         (c) 2019 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
""" Library of Congress lookup """

import re
import sys

import config
import misc.SRU as SRU

from MARC              import XML
from db.mysql.bib      import bib     as bib_db
from model.biblio.bib  import bib

db_name = 'franklin'
db = bib_db( config.CREDENTIALS['database'][db_name] )

index_regex = re.compile( r'^[\d]{1,2}$' )
MARC_regex = re.compile( r'^m[\d]{1,2}$' )

SRU_keys = {
    'l' : 'LCCN',
    't' : 'title',
    'a' : 'author',
    'i' : 'ISBN',
    's' : 'ISSN'
    };

def save_record( rec, db ):
    rec.strip_900s()
    rec.update_timestamp()
    try:
        db.add( rec )
    except mdb.IntegrityError:
        print( 'Already in catalog' )
    except mdb.ProgrammingError as e:
        print( 'SQL_error: {}'.format( e ) )


def get_prompted_input( prompt ):
    sys.stdout.write( prompt )
    sys.stdout.flush()
    try:
        val = sys.stdin.readline().strip()
    except KeyboardInterrupt:
        print()
        sys.exit( 0 )
    return val


def LC_search( args_dict ):
    query = SRU.query( args_dict )
    query.max_recs = 25;
    XML_data = query.submit()
    records = XML.parse_str( XML_data )
    bibs = []
    for i in range( len( records ) ):
        b = bib()
        b.__dict__ = records[ i ].__dict__
        bibs.append( b )
    return bibs


def select_record( records, prompt_detail ):
    for i in range( len( records ) ):
        print( "{:3} {}".format(
            i,
            records[ i ].cite()
            ) )
    cmd = get_prompted_input(  'Number of record to store' + prompt_detail )
    if index_regex.match( cmd ):
        try:
            save_record( records[ int( cmd ) ], db )
        except IndexError:
            pass
        return ''
    elif MARC_regex.match( cmd ):
        print( records[ int( cmd[ 1: ] ) ] )
    else:
        return cmd


if __name__ == "__main__":

    try:
        mode = sys.argv[ 1 ]
    except IndexError:
        mode = ''

    if mode == 'scan':

        ISBN = ''
        while True:

            if ISBN == '':
                ISBN = get_prompted_input( 'ISBN: ' )

            records = LC_search( { 'ISBN' : ISBN } )
            if records is None or len( records ) == 0:
                print( '*** not found ***' )
                ISBN = ''
                continue

            # If only one record returned, live dangerously and store it.
            if len( records ) == 1:
                print( '>>> storing record' )
                save_record( records[ 0 ], db )
                ISBN = ''
                continue

            ISBN = select_record( records, ', or next ISBN: ' )

    else:

        while True:

            type = get_prompted_input( '(L)CCN, (T)itle, (A)uthor, (I)SBN: ' );
            try:
                key = SRU_keys[ type ]
            except KeyError:
                continue

            search = get_prompted_input( key + ' search: ' )

            records = LC_search( { key : search } )
            if records is None or len( records ) == 0:
                print( '*** not found ***' )
                continue

            select_record( records, ' or Enter for none: ' )
