#!/usr/bin/env python3

import re
import sys
import MySQLdb as mdb

sys.path.append( '../lib' )

import config
import SRU
import MARC_XML
from data_bib import data_bib


db_name = 'Franklin'
db = data_bib( config.CREDENTIALS['database'][db_name] )

XML_parser = MARC_XML.MARC_XML_parser()

index_regex = re.compile( '^[\d]{1,2}$' )
marc_regex = re.compile( '^m[\d]{1,2}$' )

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
    query = SRU.Query( args_dict )
    query.max_recs = 25;
    XML_data = query.submit()
    records = XML_parser.parse_string( XML_data )
    return records


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
    elif marc_regex.match( cmd ):
        print( records[ int( cmd[ 1: ] ) ] )
    else:
        return cmd


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
