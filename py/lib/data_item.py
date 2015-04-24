#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              data_item.py
#  Description:       Data layer for Items
#  Author:            Jay Windley <jwindley>
#  Created:           Sun Mar  8 22:58:39 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------


from data_mysql import data_mysql

class data_item( mysql_driver ):

    def __init__( self, conn_data ):
        conn_data[ 'db' ] = 'Franklin'
        mysql_driver( conn_data )

    
