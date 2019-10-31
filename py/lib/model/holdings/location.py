#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              location.py
#  Description:       Franklin location objects
#  Author:            Jay Windley <jwindley>
#  Created:           Fri Apr 17 23:19:49 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""Locations for shelving"""

from misc.IND import IND

class access_policy( IND ):
    """Location Access Policy object.  This is a direct mapping from the data store, and is a strict
    ID-Name-Description object.

    This object determines the degrees of restriction that apply to a location.

    """
    pass



class shelving_scheme( IND ):
    """Shelving scheme object.  This is a direct mapping from the data store, and is a string
    ID-Name-Description object.

    The shelving scheme object determines the order of arrangement of the Items in the shelving
    location, such as by classification or for display.

    """
    pass


class location( IND ):
    """Physical location of Item at the gross geographical level.  Refers typically to a building or
    other visitable location reckoned in city addressing.

    """

    def __init__( self, **kwargs ):
        self.address1                   = ''      #
        self.address2                   = ''      #  ordinary city
        self.city                       = ''      #  addressing
        self.state                      = ''      #
        self.ZIP                        = ''      #

                                                  #
        self.geo_lat                    = 0       #  GIS addressing
        self.geo_long                   = 0       #

                                                  #  default access
        self.access_policy              = None    #  policy unless
                                                  #  overridden

        self.access_policy_ID  = None

        super( Location, self ).__init__( **kwargs )

    def get_access_policy( self ):
        if self.Location_Access_Policy is not None:
            return self.Location_Access_Policy


class sublocation( IND ):
    """Physical sub-location of Item at a fine geographical level.  Refers typically to a room or area
    within a single physical street address.

    """
    def __init__( self, **kwargs ):

        self.location                   = None    #  parent location
        self.access_policy              = None    #  overrides parent

        self.location_ID                = None
        self.Location_Access_Policy_ID  = None

        super( Sublocation, self ).__init__( **kwargs )

    def access_policy( self ):
        if self.Location_Access_Policy is not None:
            return self.Location_Access_Policy
        if self.Location is not None:
            return self.Location.access_policy()
        return None


class hhelving_location( IND ):
    """Physical shelving of Item within its sublocation, such as a specific shelving unit or area within
    a single room."""

    def __init__( self, **kwargs ):

        self.Sublocation                = None    #  parent sublocation
        self.Shelving_Scheme            = None    #  shelving schema
        self.Location_Access_Policy     = None    #  overrides parent

        self.Sublocation_ID             = None
        self.Shelving_Scheme_ID         = None
        self.Location_Access_Policy_ID  = None

        super( Shelving_Location, self ).__init__( **kwargs )

    def access_policy( self ):
        if self.Location_Access_Policy is not None:
            return self.Location_Access_Policy
        if self.Sublocation is not None:
            return self.Sublocation.access_policy()
        return None


class item_location( object ):
    def __init__( self, **kwargs ):
        self.Location           = None
        self.Sublocation        = None
        self.Shelving_Location  = None

    def access_policy( self ):
        return self.Shelving_Location.access_policy()
