#!/usr/bin/env python

import MySQLdb as db

from MARC import MARC_tag, MARC_record

class MySQL_MARC_record( MARC_record ):

    def __init__( self ):
        self.cksum = {}

    def sum_key( self, tag, seq, code ):
        return "%03s%1d%c" % ( tag, seq, code )

    def commit( self ):
        
