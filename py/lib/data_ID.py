#!/usr/bin/env python3
#-------------------------------------------------------------------------------
#  File:              data_ID.py
#  Description:       Data layer for ID-indexed tables
#  Author:            Jay Windley <jwindley>
#  Created:           Sat Apr 18 20:47:50 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
#-------------------------------------------------------------------------------
"""Data layer for ID-indexed tables"""

import MySQLdb     as     mdb
import config
from   data_mysql  import mysql_driver


class data_ID( mysql_driver ):
    """Data layer for tables whose names mimic the class names that represent them programmatically,
    whose field names are identical to the SQL column names, and whose primary key is named 'ID'.
    The zen of this data layer is that the Pytnon objects themselves provide the basis for
    formulating the SQL queries, and are polymorphic at the langauge level.
    """
    def __init__( self, conn_data ):
        conn_data[ 'db' ] = 'franklin'
        mysql_driver.__init__( self, conn_data )


    def get( self, type, ID ):
        """Retrieve an ID-indexed object of the given type."""
        d = self.get_dict_by_ID( type.__name__, ID )
        return type( **d )


    def put( self, obj ):
        """Save an ID-indexed object.  If the object already exists, it isupdated.  Otherwise it is created.
        """
        try:
            self.add_dict( obj.__class__.__name__, obj.__dict__ )
        except mdb.IntegrityError:
            self.update_dict( obj.__class__.__name__,
                              obj.__dict__,
                              'ID' )


    def delete( self, obj ):
        """Delete an ID-indexed object."""
        self.execute(
            "DELETE FROM {table} WHERE `ID` = '{val}';".format(
                table = obj.__class__.__name__,
                val = obj.ID ) )
        self.commit()
