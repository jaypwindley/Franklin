#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              location.py
#  Description:       MySQL implementation of Location CRUD
#  Author:            Jay Windley <jwindley>
#  Created:           Thu Oct 31 15:09:43 2019
#  Copyright:         (c) 2019 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
""" MySQL implementation of Location CRUD. """

from db.mysql import IND
from model.holdings import location

class access_policy( IND.IND ):
    def __init__( self, conn_data ):
        super( access_policy, self ).__init__( location.access_policy().__class__, conn_data )

class shelving_scheme( IND.IND ):
    def __init__( self, conn_data ):
        super( shelving_scheme, self ).__init__( location.shelving_scheme().__class__, conn_data )
