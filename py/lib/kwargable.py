#!/usr/bin/env python3
"""
#  File:              kwargable.py
#  Description:       Base class for objects constructed from keyword
#                     arguments
#  Author:            Jay Windley <jwindley>
#  Created:           Fri Apr 17 23:52:58 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
"""


class kwargable( object ):
    """Base class for any object constructed solely from keyword arguments, but which has a canonical
    list of members.

    The general pattern of use is to subclass this base class, then in the __init__() set the
    default values for the canonical members, and finally call the super() constructor (i.e., this
    class constructor) which first records the canonically-set member names and then populates the
    subclass object with keyword arguments.

    The members defined prior to invoking wwargable.__init__() are the canonical keys.  These are
    the only keywords that are respected by __init__.  Others may appear, but they will be ignored.

     class thing( kwargable ):
       def __init__( **kwargs ):
         self.foo = 'default foo value'              # set defaults
         self.bar = []
         super( thing, self ).__init__( **kwargs )   # call super init

     t = thing( foo = 'foo', bob = 'your uncle' )

    Keyword foo is passed in and overrides the default thing.foo.  bar is not passed and therefore
    takes on the default.  bob is accepted, but ignored because it is not already part of the class.
    """

    # list of __dict__ keys that are considered canonical for this class.
    canon = []

    def __init__( self, **kwargs ):

        # Save the canonical field names.
        kwargable.canon = self.__dict__.keys()

        # Update everything, even fields that aren't canonical.
        vars( self ).update( kwargs )

        # Erase the entries that aren't canon.
        for k in self.__dict__.keys():
            if not k in kwargable.canon:
                del self.__dict__[ k ]
