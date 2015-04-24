#!/usr/bin/env python

import sys

sys.path.append( '../lib' )
import config
import Staff
from franklin_rpc_client import Franklin_RPC_Client
from JSONRCP2 import JSONRPC2_Request

class Staff_RPC_Client( Franklin_RPC_Client ):

    def __init__( self,
                  remote_host = config.RPC[ 'staff' ][ 'host' ],
                  port = config.RPC[ 'staff' ][ 'port' ] ):
        super( Staff_RPC_Client, self ).__init__( remote_host, port )
        self.URL = '/staff'

    def search_staff( self, key_list = [] ):
        """
        Search the staff directory for logins and names listed in
        key_list.  If key_list is empty, retrieve all staff records.
        """
        pass
    
    def get_staff( self, login ):
        """
        Retrieve the staff record for the given login.
        """
        

    def edit_staff( self, session_key, login ):
        """
        Retrieve the staff record for the given login along with a
        checksum to be supplied to a subsequent store() call.  A valid
        session key is required.
        """
        pass

    def store_staff( self, session_key, staff, checksum ):
        """
        Store the given staff record.  If the record already exists,
        then a valid checksum must also be provided, produced by a
        previous call to edit() for this record.  If the record is new,
        no checksum is required.  A valid session key is required.
        """
        pass

    def delete_staff( self, session_key, login ):
        """
        Delete the staff record having the given login.
        """
        return self.send(
            self.URL,
            JSONRPC2_Request(
                'delete_staff',
                session = session_key,
                login = login ) )

    def get_dept( self, ID = None ):
        """
        Retrieve the department record with the given ID.  If no ID is
        specified, retrieve a list of departments.
        """
        

    def edit_dept( self, session_key, ID ):
        """
        Retrieve the department record with the given ID, as well as a
        checksum to be supplied to any subsequent store_dept() call.
        A valid session key is required.
        """
        pass

    def store_dept( self, session_key, dept, checksum ):
        """
        Store the department record.  If a record already exists for the
        ID embedded in the department record, a valid checksum produced
        by a previous edit_dept() call must also be supplied.  A valid
        session key is required.
        """
        pass

    def delete_dept( self, session_key, ID ):
        """
        Delete the department record having the given ID.
        """
        return self.send(
            self.URL,
            JSONRPC2_Request(
                'delete_dept',
                session = session_key,
                ID = ID ) )


    def get_role( self, ID = None ):
        pass

    def edit_role( self, session_key, ID ):
        pass

    def store_role( self, session_key, role, checksum ):
        pass

    def delete_role( self, session_key, ID ):
        pass
