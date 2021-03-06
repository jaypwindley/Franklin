#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              item.py
#  Description:       Franklin Item for holdings
#  Author:            Jay Windley <jwindley>
#  Created:           Sun Mar  8 19:59:26 2015
#  Copyright:         (c) 2015 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""Item and notes for holdings"""


class item( object ):

    def __init__( self, *args, **kwargs ):
        self.ID                  = None
        self.ctl_num             = None
        self.copy                = 1
        self.shelving_location   = None
        self.electronic_location = None
        self.content_type        = None
        self.media_type          = None
        self.carrier_type        = None
        self.notes = []


class note( object ):

    def __init__( self, *args, **kwargs ):
        self.ID         = None
        self.type       = None
        self.timestamp  = None
        self.agent      = None
        self.detail     = None
        self.actions    = {}


class action( object ):

    def __init__( self ):
        self.timestamp = None
        self.agent     = None
        self.note      = None
        self.authority = None
        self.method    = None
        self.outcome   = None
