#!/usr/bin/env python

import sys
sys.path.append( 'lib' )
import config
import Staff
from data_staff import data_staff

db_name = 'Franklin'
db = data_staff( config.CREDENTIALS['database'][db_name] )

print db.get_all_depts()
