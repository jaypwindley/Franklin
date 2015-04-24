#!/usr/bin/env python
"""
# -----------------------------------------------------------------------
#  File:              data_ID.py
#  Description:       Data layer for ID-indexed tables
#  Author:            Jay Windley <jwindley>
#  Created:           Sat Apr 18 20:47:50 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""

import MySQLdb     as     mdb
import config
from   data_mysql  import mysql_driver


#***********************************************************************
#
#  Data layer for tables whose names mimic the class names that
#  represent them programmatically, whose field names are identical to
#  the SQL column names, and whose primary key is named 'ID'.  The zen
#  of this data layer is that the Pytnon objects themselves provide the
#  basis for formulating the SQL queries, and are polymorphic at the
#  langauge level.
#
#***********************************************************************
class data_ID( mysql_driver ):

    def __init__( self, conn_data ):
        conn_data[ 'db' ] = 'Franklin'
        mysql_driver.__init__( self, conn_data )

    #-------------------------------------------------------------------
    # Retrieve an ID-indexed object of the given type.
    #
    def get_object( self, type, ID ):
        d = self.get_dict_by_ID( type.__name__, ID )
        return type( **d )


    #-------------------------------------------------------------------
    # Save an ID-indexed object.  If the object already exists, it is
    # updated.  Otherwise it is created.
    #
    def save_object( self, obj ):
        try:
            self.add_dict( obj.__class__.__name__, obj.__dict__ )
        except mdb.IntegrityError:
            self.update_dict( obj.__class__.__name__,
                              obj.__dict__,
                              'ID' )

            
    #-------------------------------------------------------------------
    # Delete an ID-indexed object.
    #
    def delete_object( self, obj ):
        self.execute(
            "DELETE FROM {table} WHERE `ID` = '{val}';".format(
                table = obj.__class__.__name__,
                val = obj.ID ) )
        self.commit()




        
if __name__ == '__main__':
    import Location
    db_name = 'Franklin'
    db = data_ID( config.CREDENTIALS['database'][db_name] )
    
    obj = db.get_object( Location.Location_Access_Policy, "R" )

    obj = Location.Shelving_Scheme( ID = 'HEAP',
                                    name = "Pile of books",
                                    description = "A disorganized pile of rubbish" )
    db.save_object( obj )
    obj.name = 'Pile'
    db.save_object( obj )
    db.delete_object( obj )
