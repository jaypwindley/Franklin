#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              TAG( data_bib.py )
#  Description:       Database driver for MySQL
#  Author:            Jay Windley <jwindley>
#  Created:           Mon May  6 16:21:47 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------

import os
import sys
import string
import MySQLdb as mdb

#
# TODO:  Exceptions
#

########################################################################
#
#  Concrete low-level database driver that simply executes queries and
#  returns results.
#
class mysql_driver( object ):

    def __init__( self, conn_data ):
        self.db = mdb.connect( conn_data['host'],
                               conn_data['user'],
                               conn_data['pass'],
                               conn_data['db'],
                               charset = 'utf8',
                               use_unicode = True )

    #-------------------------------------------------------------------
    # Return a single value that is the single row and single column
    # resulting from the given query. Returns None if the query
    # produces no value.
    #
    def single_value( self, query ):
        cur = self.db.cursor()
        cur.execute( query )
        data = cur.fetchone()
        if data is None: return None
        return data[0]


    #-------------------------------------------------------------------
    # Return an array of database rows that result from the given
    # query.  Queries that return no rows return an empty list.
    #
    def row_array( self, query ):
        cur = self.db.cursor()
        cur.execute( query )
        data = cur.fetchall()
        return data


    #-------------------------------------------------------------------
    # Return an array of dictionaries that result from the given query,
    # where the keys of each dictionary are the column names in the
    # result and the values are the corresponding retrieve values.
    #
    def row_dict( self, query ):
        cur = self.db.cursor()
        cur.execute( query )
        data = cur.fetchall()
        results = []
        cols = tuple( [ d[ 0 ] for d in cur.description ] )
        for row in data:
            results.append( dict( zip( cols, row ) ) )
        return results


    #-------------------------------------------------------------------
    # Return a row in dict form from a table having a designated ID
    # field, by the ID.
    #
    def get_dict_by_ID( self, table, ID ):
        query = "SELECT * FROM {table} WHERE `ID` = '{ID}';".format(
            table = table,
            ID = ID
            )
        return self.row_dict( query )[ 0 ]


    #-------------------------------------------------------------------
    # Add a dictionary to the given table where the dictionary indices
    # are column names and the dictionary values are intended row
    # contents.
    #
    def add_dict( self, table, dict ):
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


    #-------------------------------------------------------------------
    # Update a row in the table according to the given dictionary, whose
    # keys are the column names and key is the primary key column name.
    #
    def update_dict( self, table, dict, key ):
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



    #-------------------------------------------------------------------
    # Execute a query.  Results are stored in the cursor object
    # associated with the connection object.
    #
    def execute( self, query ):
        cur = self.db.cursor()
        cur.execute( query )


    #-------------------------------------------------------------------
    # Commit any pending transactions.
    #
    def commit( self ):
        self.db.commit()


    # ------------------------------------------------------------------
    # Escape the string for use as a single-quoted value in an INSERT
    # statement.
    #
    def esc( self, s ):
        if isinstance( s, str ):
            return s.replace( "'", "\\'" )
        else:
            return s
