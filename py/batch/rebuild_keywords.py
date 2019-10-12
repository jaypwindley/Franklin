#!/usr/bin/env python3

import re
import sys
import MySQLdb as mdb

sys.path.append( '../lib' )

import config
from data_bib import data_bib

db_name = 'franklin'
db = data_bib( config.CREDENTIALS['database'][db_name] )

SPLIT_REGEX = re.compile( r'[ ~\,\-]' )

# May remove parts of words or entire words.  Since each regex is applied in turn, carefully order
# the regexes so that the effects of applying one regex are properly susceptible to matching
# subsequent expressions.
DELETE_REGEXES = list( map( re.compile, [
    r'\d{1,2}(/\d{1,2})?$',        # short digit strings
    r"['\:\,\.\/\[\]\(\)]+",       # remove lots of punctuations
    r'[\"]+',                      # ...and more punctuation
    r'^[a-z0-9]{1}$',              # single alphanumeric characters
    ] ) )

# Remove entire literal strings, no regex matching
DELETE_LITERALS = [
    '!', "'", '&', '#', '-', '/', 'a', '1.', ':',
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
    """
    Return a list of keyword/offset pairs for the keywords in str
    """
    result = []
    words = re.split( SPLIT_REGEX, str.lower() )
    offset = 0
    for w in [ it for it in words if it not in DELETE_LITERALS ]:
        for r in DELETE_REGEXES:
            w = re.sub( r, '', w )
        if w != '':
            result.append( { 'word' : w, 'offset' : offset } )
            offset = offset + 1
    return [ it for it in result if it[ 'word' ] not in DELETE_LITERALS ]


def store_keyword_tuples( ctl_num, words, namespace, instance = 0 ):
    """
    Store words in database under the key suggested by ctl_num, namespace, and instance
    """
    for w in words:
        t = { 'ctl_num'    : ctl_num,
              'keyword'    : w[ 'word' ],
              'namespace'  : namespace,
              'instance'   : instance,
              'offset'     : w[ 'offset' ] }
        try:
            db.add_dict( 'bib_keywords', t )
        except mdb.IntegrityError:
            pass


if __name__ == "__main__":

    # Clear current keyword entries; we will rebuild from scratch.
    db.clear_keywords()

    # @todo This isn't going to work right until the traversal is made to work right.  The titles
    # will be missing subtitles because we can't join on a and b fields.  Authors will be mixed
    # together.  Subjects will be mixed together.

    for title in db.get_all_titles():
        store_keyword_tuples(
            title[ 0 ],
            extract_keywords( title[ 1 ] ),
            'T' )
    db.commit()

    for author in db.get_all_authors():
        store_keyword_tuples(
            author[ 0 ],
            extract_keywords( author[ 2 ] ),
            'A' )
    db.commit()

    for subject in db.get_all_subjects():
        store_keyword_tuples(
            subject[ 0 ],
            extract_keywords( subject[ 2 ] ),
            'S' )
    db.commit()

    sys.exit( 0 )
