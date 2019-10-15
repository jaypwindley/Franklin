#!/usr/bin/env python3
"""
# -----------------------------------------------------------------------
#  File:              config.py
#  Description:       Installation dependent configuration
#  Author:            Jay Windley <jwindley>
#  Created:           Fri Sep  6 16:05:16 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""

DEBUG = 0

# ------------------------------------------------------------------------
# Host access user names and passwords.
#
CREDENTIALS = {
    'database': {
        'franklin': {
            'host': 'kibbles',
            'user': 'biblio',
            'pass': 'silence_dogood'
            },
        }
    }


REST = {
    'host'     : 'localhost',
    'port'     : '1138',
    'version'  : '1'
    }

API = {
    'root'     : '/api/v' + REST[ 'version' ] + '/',
    'features' : [ 'auth', 'bib' ]
    }

def API_URL( tail ):
    return 'http://' + REST['host'] + ':' + REST['port'] + API[ 'root' ] + tail

HOME = '/home/jwindley/src/Franklin/'

PATHS = {
    'spool' : {
        'MARC': HOME + 'spool/MARC/',
        'XML' : HOME + 'spool/XML/'
        },
    'lib'  : HOME + 'py/lib',
    'data' : HOME + 'Data/',
    'log'  : {
        'bib' : '/tmp/log'
        }
    }

#-----------------------------------------------------------------------
# Parameters for SRU searches at Library of Congress.
#
SRU = {
    'host'    : 'lx2.loc.gov',
    'port'    : 210,
    'path'    : '/LCDB',
    'url'     : 'http://lx2.loc.gov:210/LCDB',

    'version' : '1.1',
    'search'  : {
        'op'       : 'searchRetrieve',
        'max_recs' : 7,
        'schema'   : 'marcxml'
        },
    'timeout' : 30                   # seconds
    }
