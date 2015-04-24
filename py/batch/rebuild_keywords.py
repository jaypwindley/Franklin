#!/usr/bin/env python

import re
import sys
import MySQLdb as mdb

sys.path.append( '../lib' )

import config
from data_bib import data_bib

db_name = 'Franklin'
db = data_bib( config.CREDENTIALS['database'][db_name] )

SPLIT_REGEX = re.compile( '[ ~\,\-]' )

DELETE_REGEXES = map( re.compile, [
    "'\d{1,2}(/\d{1,2})?$",       # short digit strings
    "['\:\,\.\/\[\]\(\)]{1,2}",   # remove lots of punctuations
    "^[a-z0-9]{1}$",              # single alphanumeric characters
    ] )

DELETE_LITERALS = [
    '!', "'", '&', '#', '-', '/',
    'a', '1.',
    'and',
    'etc',
    'for',
    'from',
    'in',
    'of',
    'on',
    'the',
    'to',
]

def extract_keywords( str ):
    result = []
    words = re.split( SPLIT_REGEX, str.lower() )
    for w in [ it for it in words
               if it not in DELETE_LITERALS ]:
        for r in DELETE_REGEXES:
            w = re.sub( r, '', w )
        if w != '':
            result.append( w )
    return list( set( [
        it for it in result
        if it not in DELETE_LITERALS
        ] ) )


def store_keyword_tuples( ctl_num, words, domain ):
    for w in words:
        t = { 'ctl_num' : ctl_num,
              'keyword' : w,
              'domain'  : domain }
        try:
            db.add_dict( 'Bib_Keywords', t )
        except mdb.IntegrityError:
            pass

db.execute( 'DELETE FROM Bib_Keywords' )

for title in db.get_all_titles():
    store_keyword_tuples(
        title[ 0 ],
        extract_keywords( title[ 1 ] ),
        'T'
    )
db.commit()

for author in db.get_all_authors():
    store_keyword_tuples(
        title[ 0 ],
        extract_keywords( author[ 2 ] ),
        'A'
    )
db.commit()

for subject in db.get_all_subjects():
    store_keyword_tuples(
        title[ 0 ],
        extract_keywords( subject[ 2 ] ),
        'S'
    )
db.commit()

sys.exit( 0 )
