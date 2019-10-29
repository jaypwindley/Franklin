#!/usr/bin/env python3
#-------------------------------------------------------------------------------
#  File:              IND.py
#  Description:       Base class for ID-Name-Description objects
#  Author:            Jay Windley <jwindley>
#  Created:           Fri Apr 17 23:25:32 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
#-------------------------------------------------------------------------------

from kwargable import kwargable


class IND( kwargable ):
    """Base class for any of several objects that consist of (or include) an ID, a name, and a
    description.

    N.B., it is rather important that all subclass constructors explicitly call the super class
    constructor.

    """

    def __init__( self, **kwargs ):

        """kwargable constructor pattern.  Set the defaults for the canonical fields and then override them
        as needed from the constructor arguments.

        """
        self.ID           = None
        self.name         = ''
        self.description  = ''
        super( IND, self ).__init__( **kwargs )

    def __str__( self ): return self.name
