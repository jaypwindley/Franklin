#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              CRUD.py
#  Description:       Database layer abstract base
#                     (C)reate, (R)ead, (U)pdate, (D)elete
#  Author:            Jay Windley <jwindley>
#  Created:           Tue Oct 29 15:47:49 2019
#  Copyright:         (c) 2019 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""Data layer abstract base: Create, Read, Update, Delete """

from abc import ABC, abstractmethod

class duplicate( Exception ):
    """ Create called on existing object """
    pass

class not_found( Exception ):
    """ Object not found """
    pass


class base( ABC ):
    """Readers and writers for Model objects must implmement the following operations."""

    @abstractmethod
    def create( self, obj, ID = None ):
        """Create a new object in the persistent store.  Return the primary key ID of the newly-created
        object.  If ID is specified, it must be used as the primary key of the object.  Otherwise
        the primary key ID is derived from the object by the implementation.  Raises exception
        'duplicate' if the object already exists in the persistent store.

        """
        pass

    @abstractmethod
    def read( self, ID: str ):
        """Read from the persistsent store the object having the given ID. Raise not_found if the object
        doesn't exist in the persistent store.

        """
        pass

    @abstractmethod
    def update( self, obj, ID = None ):
        """Update the object in the persistent store.  If the ID is specified, it is the primary key of the
        object to be updated.  Otherwise the implementation may derive the primary key from th e
        object.  Raises exception 'not_found' if the object doesn't exist in the persistent store.
        The implementation may selectively update only the portions of the persistent store that it
        detects have changed.

        """
        pass

    @abstractmethod
    def delete( self, ID: str ):
        """Delete the object having the given ID.  Raises not_found if the object having the given ID is
        not found inthe persistent store.

        """
        pass
