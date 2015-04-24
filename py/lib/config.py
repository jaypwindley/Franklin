#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              config.py
#  Description:       Installation dependent configuration
#  Author:            Jay Windley <jwindley>
#  Created:           Fri Sep  6 16:05:16 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------

DEBUG = 0

RPC = {
    'bib': {
        'host': 'localhost',
        'port': 1138
        },
    'staff': {
        'host': 'localhost',
        'port': 1138
        }
    }

# ------------------------------------------------------------------------
# Host access user names and passwords.
# 
CREDENTIALS = {
    'database': {
        'Franklin': {
            'host': 'absinthe',
            'user': 'biblio',
            'pass': 'silence_dogood'
            },
        }
    }

HOME = '/home/jwindley/Dropbox/Projects/Franklin/'

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
