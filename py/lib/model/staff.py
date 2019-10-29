#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              data_staff.py
#  Description:       Data layer for Staff etc. objects
#  Author:            Jay Windley <jwindley>
#  Created:           Sun Mar  8 20:44:20 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------

import Staff
from data_mysql import mysql_driver



def db_to_obj_keys( orig, keymap ):
    revised = {}
    for k in orig:
        try:
            revised[ keymap[ k ] ] = orig[ k ]
        except KeyError:
            revised[ k ] = orig[ k ]
    return revised




class data_staff( mysql_driver ):

    dept_map = { 'Location_ID' : 'location' }
    
    def __init__( self, conn_data ):
        conn_data[ 'db' ] = 'Franklin'
        mysql_driver.__init__( self, conn_data )



        
    def get_staff_by_login( self, login ):
        query = """
                SELECT *
                FROM   Staff
                WHERE  login = '{login}'
                LIMIT  1;
                """.format( login = login )
        vals = self.row_dict( query )
        if vals: vals = vals[ 0 ]
        dude = Staff.Staff( **vals )

        query = """
                SELECT *
                FROM   Staff_Role_Map
                WHERE  login = '{login}';
                """.format( login = login )

        roles = self.row_dict( query )
        if roles:
            for role in roles:
                dude.roles.append( role[ 'Staff_Role_ID' ] )
        return dude



    def put_staff( self, item ):
        pass


    
    def get_dept( self, ID ):
        query = """
                SELECT *
                FROM   Staff_Department
                WHERE  ID = '{ID}'
                LIMIT  1;
                """.format(
                    ID = ID
                )
        vals = self.row_dict( query )
        if vals: vals = vals[ 0 ]
        
        vals = db_to_obj_keys( vals, self.dept_map )
        print vals
        return Staff.Department( vals )


    
    def put_dept( self, dept ):
        pass


    
    def get_all_depts( self ):
        query = 'SELECT * FROM Staff_Department;'
        vals = self.row_dict( query )
        return vals


    
    def get_role( self, ID ):
        query = """
                SELECT *
                FROM   Staff_Role
                WHERE  ID = '{ID}'
                LIMIT 1;
                """.format( ID = ID )
        vals = self.row_dict( query )
        return vals[ 0 ]


    
    def put_role( self, role ):
        pass



    def get_all_roles( self ):
        query = """
                SELECT *
                FROM   Staff_Role;
                """
        vals = self.row_dict( query )
        return vals
