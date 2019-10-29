#!/usr/bin/env python

from data_ID import data_ID
import Location

class Location_Factory( object ):

    def __init__( self, db = None ):
        self.db = db


    def get( self, shelving_loc ):
        """Get a fully-specified item location from the data store."""

        loc = Location.Item_Location()

        try:

            # Get shelving location.
            sh_loc = self.db.get( Location.Shelving_Location, shelving_loc )

            # Get sublocation.
            if sh_loc.Sublocation_ID is not None:
                subloc = self.db.get( Location.Sublocation, sh_loc.Sublocation_ID )

            # Get location.
            if subloc.Location_ID is not None:
                location = self.db.get( Location.Location, subloc.Location_ID )

        except IndexError:
            return loc

        # Aggregate the findings.
        loc.Shelving_Location  = sh_loc
        loc.Sublocation        = subloc
        loc.Location           = location

        # Fill in the access policies.
        for k in loc.__dict__.keys():
            policy_ID = loc.__dict__[ k ].Location_Access_Policy_ID
            if policy_ID is not None:
                policy = self.db.get_object(
                    Location.Location_Access_Policy,
                    policy_ID )
                loc.__dict__[ k ].Location_Access_Policy = policy

        return loc


    def get_access_policy( self, ID ):
        """Retrieve the access policy by ID."""
        if ID is None: return None
        return self.db.get( Location.Location_Access_Policy, ID )
