#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              TAG( data_bib.py )
#  Description:       Database driver for MySQL
#  Author:            Jay Windley <jwindley>
#  Created:           Mon May  6 16:21:47 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""Low-lovel MySQL driver"""

import os
import sys
import string
import MySQLdb as mdb

def esc( self, s: str ) -> str:
    """Escape the string for use as a single-quoted value in an INSERT statement."""
    if isinstance( s, str ):
        return s.replace( "'", "\\'" )
    else:
        return s


class base( object ):

    def __init__( self, conn_data: dict ):
        self.db = mdb.connect(
            conn_data['host'],
            conn_data['user'],
            conn_data['pass'],
            conn_data['db'],
            charset = 'utf8',
            use_unicode = True )


class reader( base ):
    """Read-only access to database"""

    def __init__( self, conn_data: dict ):
        super( reader, self ).__init__( **kwargs )

    def single_value( self, query: str ):
        """Return a single value that is the single row and single column resulting from the given
        query. Returns None if the query produces no value.

        """
        cur = self.db.cursor()
        cur.execute( query )
        data = cur.fetchone()
        if data is None: return None
        return data[0]


    def row_array( self, query: str ) -> list:
        """Return a list of database rows that result from the given query.  Queries that return no rows
        return an empty list.

        """
        cur = self.db.cursor()
        cur.execute( query )
        data = cur.fetchall()
        return data


    def row_dict( self, query: str ) -> list:
        """Return an array of dictionaries that result from the given query, where the keys of each
        dictionary are the column names in the result and the values are the corresponding retrieve
        values.

        """
        cur = self.db.cursor()
        cur.execute( query )
        data = cur.fetchall()
        results = []
        cols = tuple( [ d[ 0 ] for d in cur.description ] )
        for row in data:
            results.append( dict( zip( cols, row ) ) )
        return results


    def get_dict_by_ID( self, table: str, ID: str ) -> dict:
        """Return a row in dict form from a table having a designated ID field, by the ID."""
        query = "SELECT * FROM {table} WHERE `ID` = '{ID}';".format(
            table = table,
            ID = ID
            )
        return self.row_dict( query )[ 0 ]


    def execute( self, query: str ):
        """Execute a query.  Results are stored in the cursor object associated with the connection
        object.

        """
        cur = self.db.cursor()
        cur.execute( query )




class reader_writer( reader ):
    """Read-write access to database"""

    def __init__( self, conn_data: dict ):
        super( reader_writer, self ).__init__( **kwargs )

    def add_dict( self, table: str, dict: dict ):
        """Add a dictionary to the given table where the dictionary indices are column names and the
        dictionary values are intended row contents.

        """
        indices = dict.keys()
        values = dict.values()
        self.execute(
            "INSERT INTO {table} ( {indices} ) VALUES ( {values} );"
            .format(
                table = table,
                indices = ', '.join( map( self.esc, indices ) ),
                values = ', '.join( map(
                    lambda x:
                        "'{}'".format( self.esc( x ) ),
                    values ) ) ) )
        self.commit()


    def update_dict( self, table: str, dict: dict, key: str ):
        """Update a row in the table according to the given dictionary, whose keys are the column names and
        key is the primary key column name.

        """
        indices = dict.keys()
        self.execute(
            "UPDATE {table} SET {assigns} WHERE `{key}` = '{val}';".format(
                table = table,
                assigns = ', '.join( map(
                    lambda idx:
                       "`{col}`='{val}'".format(
                           col = idx,
                           val = self.esc( dict[ idx ] ) ),
                    indices ) ),
                key = key,
                val = dict[ key ] ) )
        self.commit()


    def commit( self ):
        """Commit any pending transactions."""
        self.db.commit()
