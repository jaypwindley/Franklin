#!/usr/bin/env python
"""
# -----------------------------------------------------------------------
#  File:              Location.py
#  Description:       Franklin Location objects
#  Author:            Jay Windley <jwindley>
#  Created:           Fri Apr 17 23:19:49 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""

from IND import IND

#***********************************************************************
#
#  Location Access Policy (LAP) object.  This is a direct mapping from
#  the data store, and is a strict ID-Name-Description object.
#
#  The LAP object determines the degress of restriction that apply to a
#  location.
#
#***********************************************************************
class Location_Access_Policy( IND ): pass



#***********************************************************************
#
#  Shelving Scheme (SS) object.  This is a direct mapping from the data
#  store, and is a string ID-Name-Description object.
#
#  The SS object determines the order of arrangement of the Items in the
#  shelving location, such as by classification or for display.
#
#***********************************************************************
class Shelving_Scheme( IND ): pass



#***********************************************************************
#
#  Physical location of Item at the gross geographical level.  Refers
#  typically to a building or other visitable location reckoned in city
#  addressing.
#
#***********************************************************************
class Location( IND ):
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
        self.Location_Access_Policy     = None    #  policy unless
                                                  #  overridden

        self.Location_Access_Policy_ID  = None
        
        super( Location, self ).__init__( **kwargs )

    def access_policy( self ):
        if self.Location_Access_Policy is not None:
            return self.Location_Access_Policy


        
#***********************************************************************
#
#  Physical sub-location of Item at a fine geographical level.  Refers
#  typically to a room or area within a single physical street address.
#
#***********************************************************************
class Sublocation( IND ):
    def __init__( self, **kwargs ):
        
        self.Location                   = None    #  parent location
        self.Location_Access_Policy     = None    #  overrides parent

        self.Location_ID                = None
        self.Location_Access_Policy_ID  = None

        super( Sublocation, self ).__init__( **kwargs )

    def access_policy( self ):
        if self.Location_Access_Policy is not None:
            return self.Location_Access_Policy
        if self.Location is not None:
            return self.Location.access_policy()
        return None


        
#***********************************************************************
#
#  Physical shelving of Item within its sublocation, such as a specific
#  shelving unit or area within a single room.
#
#***********************************************************************
class Shelving_Location( IND ):
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




class Item_Location( object ):
    def __init__( self, **kwargs ):
        self.Location           = None
        self.Sublocation        = None
        self.Shelving_Location  = None

    def access_policy( self ):
        return self.Shelving_Location.access_policy()

