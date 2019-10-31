#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              staff.py
#  Description:       CRUD implementation for staff
#  Author:            Jay Windley <jwindley>
#  Created:           Thu Oct 31 14:42:19 2019
#  Copyright:         (c) 2019 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
""" MySQL implementation of CRUD for library staff. """

from model.biblio import staff
from db import CRUD

class staff( CRUD.base ):
    pass
