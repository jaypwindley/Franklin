#!/usr/bin/python3
# -----------------------------------------------------------------------
#  File:              IND.py
#  Description:       MySQL implementation of ID-Name-Description CRUD
#  Author:            Jay Windley <jwindley>
#  Created:           Thu Oct 31 15:18:51 2019
#  Copyright:         (c) 2019 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
""" MySQL implementation of ID-Name-Description CRUD. """

from db import CRUD
from db.mysql import driver
from misc import IND

class IND( CRUD.base ):

    def __init__( self, c, conn_data: dict ):
        self.table = c.__name__
        self.create_type = c
        self.db = driver.reader_writer( conn_data )

    def create( self, obj: IND.IND, ID = None ):
        self.db.add_dict( self.table, obj.__dict__ )
        return obj.ID

    def read( self, ID: str ):
        vals = self.db.get_dict_by_ID( self.table, ID )
        obj = self.create_type( **vals )
        return obj

    def update( self, obj: IND.IND, ID = None ):
        pass

    def delete( self, ID: str ):
        self.db.delete( self.name, 'ID', ID )
