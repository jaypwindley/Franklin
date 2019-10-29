#!/usr/bin/env python3
#-------------------------------------------------------------------------------
#  File:              ID.py
#  Description:       Data layer for ID-indexed tables
#  Author:            Jay Windley <jwindley>
#  Created:           Sat Apr 18 20:47:50 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
#-------------------------------------------------------------------------------
"""Data layer for ID-indexed tables"""

import MySQLdb     as     mdb
import driver

import sys
sys.path.append( '..' )

import CRUD
# import config


class ID( CRUD.base ):
    """Data layer for objects that satisfy the following criteria:

    - The class identifier of the object is the MySQL table name
    - The canonical member names of the object are their corresponding column names.
    - The primary key column is named 'ID'

    The zen of this data layer is that the Pytnon objects themselves provide the basis for
    formulating the SQL queries, and are polymorphic at the langauge level.  This may be bad for
    obvious reasons of coupling.

    See misc/IND.py

    """
    def __init__( self, conn_data ):
        #conn_data[ 'db' ] = 'franklin'
        #mysql_driver.__init__( self, conn_data )
        pass

    def read( self, ID: str ) -> dict:
        #d = db.get_dict_by_ID( type.__name__, ID )
        #return type( **d )
        pass

    def put( self, obj ):
        """Save an ID-indexed object.  If the object already exists, it isupdated.  Otherwise it is created.
        """
        #try:
        #    self.add_dict( obj.__class__.__name__, obj.__dict__ )
        #except mdb.IntegrityError:
        #    self.update_dict( obj.__class__.__name__,
        #                      obj.__dict__,
        #                      'ID' )
        pass

    def delete( self, ID: str ):
        db.delete( ID, self.__class__.__name__, "ID", self.ID )
#    def delete( self, obj ):
#        """Delete an ID-indexed object."""
        #self.execute(
        #"DELETE FROM {table} WHERE `ID` = '{val}';".format(
        #        table = obj.__class__.__name__,
        #        val = obj.ID ) )
        #self.commit()
#        pass
