#!/usr/bin/env python
"""
# -----------------------------------------------------------------------
#  File:              Staff.py
#  Description:       Library staff
#  Author:            Jay Windley <jwindley>
#  Created:           Sun Mar  8 20:36:52 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""

import sys
sys.path.append( '../lib' )
from IND import IND

#***********************************************************************
#
#  Staff personnel.
#
#***********************************************************************
class Staff( object ):

    def __init__( self, *args, **kwargs ):
        self.roles      = []
        self.login      = ''
        self.last_name  = ''
        self.first_name = ''
        self.title      = ''
        self.dept       = ''
        
        if kwargs:
            for k in kwargs:
                try:
                    self.__dict__[ k ] = kwargs[ k ]
                except KeyError: pass


#***********************************************************************
#
#  Departments in which staff are organized.
#
#***********************************************************************
class Department( IND ):

    def __init__( self, **kwargs ):
        self.location    = ''
        super( Department, self ).__init__( **kwargs )

