#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              staff.py
#  Description:       Library staff
#  Author:            Jay Windley <jwindley>
#  Created:           Sun Mar  8 20:36:52 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""Library staff"""

from IND import IND

import sys
sys.path.append( '..' )
from misc import kwargable as kw

class staff( kw.kwargable ):
    """Staff who work at the library, specifically not patrons"""

    def __init__( self, *args, **kwargs ):
        self.roles      = []
        self.login      = ''
        self.last_name  = ''
        self.first_name = ''
        self.title      = ''
        self.dept       = ''
        super( staff, self ).__init__( **kwargs )


class department( IND ):
    """Departments in which staff are organized"""
    def __init__( self, **kwargs ):
        self.location    = ''
        super( department, self ).__init__( **kwargs )