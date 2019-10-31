#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              bib.py
#  Description:       CRUD wrapper for bibliographic records
#  Author:            Jay Windley <jwindley>
#  Created:           Thu Oct 31 13:35:59 2019
#  Copyright:         (c) 2019 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
""" CRUD implementation of CRUD for bibliographic records; type sugar for MARC """

from db           import CRUD
from db.mysql     import MARC
from model.biblio import bib

class bib( CRUD.base ):

    def __init__( self, conn_data ):
        self.MARC = MARC.MARC( conn_data )

    def create( self, obj: bib, ID = None ):
        return self.MARC.create( obj )

    def read( self, ID: str ):
        return self.MARC.read( ID )

    def update( self, obj: bib, ID = None ):
        self.MARC.update( bib )

    def delete( self, ID: str ):
        self.MARC.delete( ID )
