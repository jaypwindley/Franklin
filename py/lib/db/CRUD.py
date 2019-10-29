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

class base( ABC ):
    """Readers and writers for Model objects must implmement the following operations."""

    @abstractmethod
    def create( self, values: dict, ID = '' ):
        """ Save a new object having the given values, optionally under the given ID"""
        pass

    @abstractmethod
    def read( self, ID: str ) -> dict:
        """ Read the object having the given ID. """
        pass

    @abstractmethod
    def read_field( self, ID: str, field: str ) -> str:
        """ Read the named field from the object having the given ID. """
        pass

    @abstractmethod
    def update( self, ID: str, values: dict ):
        """ Update the object having the given ID using the given values (need not be complete)"""
        pass

    @abstractmethod
    def delete( self, ID: str ):
        """ Delete the object having the given ID """
        pass
