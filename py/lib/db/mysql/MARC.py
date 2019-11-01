#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              TAG( MARC.py )
#  Description:       CRUD implementation for bibliographic records
#  Author:            Jay Windley <jwindley>
#  Created:           Mon May  6 16:21:47 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""CRUD implementation for MySQL storage of MARC 21 records."""

import os
import sys

import MySQLdb as mdb

from misc.switch          import switch
from db                   import CRUD
from MARC                 import MARC
from db.mysql             import driver
from db.mysql.driver      import esc


class MARC( CRUD.base ):
    """ Translate CRUD operations into MySQL driver operations. """

    def __init__( self, conn_data ):
        # @todo Does this need to access a global pool of database connections?
        # Attempt to connect to database.
        conn_data['db'] = 'franklin'
        self.db = driver.reader_writer( conn_data )


    def create( self, obj: MARC.record, ID = None ):
        try:
            self.insert_leader( obj.ctl_num(), obj.leader )
            self.add_tags( obj )
            return obj.ctl_num()
        except mdb.IntegrityError:
            raise CRUD.duplicate


    def read( self, ID: str ):
        rec = MARC.record()
        rec.leader = self.get_leader( ID )
        if rec.leader is None:
            raise CRUD.not_found
        self.build_record( rec, ID )
        return rec


    def update( self, obj: MARC.record, ID = None ):
        pass


    def delete( self, ID: str ):
        try:
            self.delete_leader( ID )
            self.db.commit()
        except db.IntegrityError:
            raise not_found



    #-------------------------------------------------------------------
    # Commit an existing record to the data store after editing.  The
    # checksum is the value returned by MARC.digest() function on the
    # record prior to editing.  If the submitted checksum does not match
    # the checksum computed on the existing record, the commit fails.
    #
    def edit_commit( self, rec, checksum ):

        # Get the original record and compute its checksum.
        base_rec = self.view( rec.ctl_num() )
        sum = base_rec.digest()
        if sum != checksum: raise ValueError( 'stale checksum' )

        # Cannot delete MARC Leader because of foreign key constraints.
        # Update the Leader instead.
        #
        self.update_leader( rec.ctl_num(), rec.leader )

        # Delete all the subordinate information from the data store,
        # then re-add it.
        #
        self.delete_all_indicators(     rec.ctl_num() )
        self.delete_all_control_fields( rec.ctl_num() )
        self.delete_all_fields(         rec.ctl_num() )
        rec.update_timestamp()
        self.add_tags( rec )

        self.commit()


    def add_tags( self, rec: MARC.record ):
        """ Add all the tags for this record. """
        for tag in rec.ctl_fields.keys():
            self.insert_control_field(
                rec.ctl_num(),
                tag,
                rec.ctl_fields[ tag ] )
        for t in rec.tags:
            if t.tag[ 0 ] != '9':
                self.insert_indicators(
                    rec.ctl_num(),
                    t.tag,
                    t.seq,
                    t.ind )
                for pos, f in enumerate( t.fields.fields ):
                    self.insert_field(
                        rec.ctl_num(),
                        t.tag,
                        t.seq,
                        f[ 0 ],
                        pos + 1,
                        f[ 1 ] )
        self.db.commit()


    def build_record( self, rec: MARC.record, ctl_num: str ):
        """Populates a record with information from the dataabase.  This ensures all records are built
        uniformly.

        """

        # Retreive control fields.
        for f in self.get_control_fields( ctl_num ):
            rec.ctl_fields[ f[0] ] = f[1]

        # Retrieve tags.  Assumes tags are returned in tag and
        # sequence order.  There is a row returned for each subfield,
        # so sequences of rows may contain the same tag and sequence.
        #
        #   f[ 0 ] = tag
        #   f[ 1 ] = seq
        #   f[ 2 ] = code
        #   f[ 3 ] = pos      Do not use as index
        #   f[ 4 ] = val
        #
        last_tag = ''
        last_seq = 0
        for f in self.get_fields( ctl_num ):
            if ( f[0] != last_tag ) or ( f[1] != last_seq ):
                t = MARC_tag( tag = f[0],
                              seq = f[1],
                              ind = self.get_indicators( ctl_num, f[0], f[1] ) )
                rec.tags.append( t )
                last_tag = f[0]
                last_seq = f[1]
            t.fields.append( f[ 2 ], f[ 4 ] )


    # Everything above here is database independent and could be factored into a higher-level API.
    # Everyting below here is SQL-specific.  None of the functions below run a commit on the
    # database.


    def get_leader( self, ctl_num: str ) -> str:
        """Get the MARC leader for the given control number, or None if no such record exists."""
        return self.db.single_value(
            """SELECT   val
            FROM     MARC_leader
            WHERE    ctl_num = '{}';""".
            format( ctl_num ) )


    def get_control_fields( self, ctl_num ) -> list:
        """Get the control fields for the record associated with the given control number, or an empty array
        if no control fields are found.  Each element is further an array where [0] is the tag and
        [1] is the value.

        """
        return self.db.row_array(
            """SELECT  tag, val
            FROM    MARC_control_fields
            WHERE   ctl_num = '{}';""".
            format( ctl_num ) )


    def get_indicators(
            self,
            ctl_num : str,
            tag     : str,
            seq     : int      ) -> str:
        """Get the indicators for the tag and sequence in the record associated with the given control
        number.  If there are no explicit indicators, return ' '.

        """
        ind = '  '
        data = self.db.row_array(
            """SELECT
                 ind_1, ind_2
               FROM
                 MARC_indicators
               WHERE
                     ctl_num = '{ctl_num_val}'
                 AND tag     = '{tag_val}'
                 AND seq     = {seq_val};""".
            format( ctl_num_val = ctl_num,
                    tag_val     = tag,
                    seq_val     = seq ) )
        if len( data ) > 0:
            ind = "%1s%1s" % ( data[0] )
        return ind


    def get_fields( self, ctl_num: str ) -> list:
        """Get the tag subfields for the record associated with the given control number, or an empty array
        if no such record exists.  Each array element is (tag, seq, code, pos, val).  Subfields are
        returned in order such that tags increase monotonically, sequence numbers increase
        monotonically within each range of tags, and pos(itions) increase monotonically within each
        individual sequenced tag.

        """
        return self.db.row_array(
            """SELECT
                 tag, seq, code, pos, val
               FROM
                 MARC_fields
               WHERE
                 ctl_num = '{}'
               ORDER BY     tag
                        AND seq
                        AND pos;""".
            format( ctl_num ) )


    def insert_leader(
            self,
            ctl_num : str,
            val     : str ):
        self.db.execute(
            """INSERT INTO MARC_leader (
                 `ctl_num`,
                  `val`
               ) VALUES (
                 '{ctl_num}',
                 '{val}' );""".
            format( ctl_num = ctl_num, val = val ) )

    def update_leader(
            self,
            ctl_num : str,
            val     : str ):
        self.db.execute(
            """UPDATE  MARC_leader
               SET     `val` = '{val}'
               WHERE   `ctl_num` = '{ctl_num}';""".
            format( ctl_num = ctl_num, val = val ) )

    def delete_leader( self, ctl_num: str ):
        self.db.execute(
            "DELETE FROM MARC_leader WHERE `ctl_num` = '{ctl_num}';"
            .format( ctl_num = ctl_num ) )

    def insert_control_field(
            self,
            ctl_num : str,
            tag     : str,
            val     : str ):
        self.db.execute(
            """INSERT INTO MARC_control_fields (
                 `ctl_num`,
                 `tag`,
                 `val`
               ) VALUES (
                 '{ctl_num}',
                 '{tag}',
                 '{val}'
               );""".
            format( ctl_num = ctl_num,
                    tag     = tag,
                    val     = val ) )

    def update_control_field(
            self,
            ctl_num : str,
            tag     : str,
            val     : str ):
        self.db.execute(
            """UPDATE MARC_control_fields
               SET `val` = '{val}'
               WHERE     `ctl_num` = '{ctl_num}'
                     AND `tag`     = '{tag}';""".
            format( ctl_num = ctl_num,
                    tag     = tag,
                    val     = val ) )

    def delete_control_field(
            self,
            ctl_num : str,
            tag     : str ):
        self.db.execute(
            """DELETE FROM MARC_control_fields
               WHERE     `ctl_num` = '{ctl_num}'
                     AND `tag`     = '{tag}';""".
            format( ctl_num = ctl_num,
                    tag_val = tag ) )

    def delete_all_control_fields( self, ctl_num: str ):
        self.db.execute(
            """DELETE FROM MARC_control_fields
               WHERE `ctl_num` = '{ctl_num}';""".
            format( ctl_num = ctl_num ) )

    def insert_indicators(
            self,
            ctl_num : str,
            tag     : str,
            seq     : int,
            ind     : str ):
        self.db.execute(
            """INSERT INTO MARC_indicators (
                 `ctl_num`,
                 `tag`,
                 `seq`,
                 `ind_1`,
                 `ind_2`
               ) VALUES (
                 '{ctl_num}',
                 '{tag}',
                  {seq},
                 '{ind_1}',
                 '{ind_2}'
               );""".
            format( ctl_num = ctl_num,
                    tag     = tag,
                    seq     = seq,
                    ind_1   = ind[0:1],
                    ind_2   = ind[1:2] ) )

    def update_indicators(
            self,
            ctl_num : str,
            tag     : str,
            seq     : int,
            ind     : str ):
        self.db.execute(
            """UPDATE MARC_indicators
               SET
                 `ind_1` = '{ind_1}',
                 `ind_2` = '{ind_2}'
               WHERE     `ctl_num` = '{ctl_num}'
                     AND `tag`     = '{tag}'
                     AND `seq`     = {seq};""".
            format( ctl_num = ctl_num,
                    tag   = tag,
                    seq   = seq,
                    ind_1 = ind[0:1],
                    ind_2 = ind[1:2] ) )

    def delete_indicators(
            self,
            ctl_num : str,
            tag     : str,
            seq     : int ):
        self.db.execute(
            """DELETE FROM MARC_indicators
               WHERE     `ctl_num` = '{ctl_num}'
                     AND `tag`     = '{tag}'
                     AND `seq`     =  {seq};""".
            format( ctl_num = ctl_num,
                    tag     = tag,
                    seq     = seq ) )

    def delete_all_indicators( self, ctl_num: str ):
        self.db.execute(
            """DELETE FROM MARC_indicators
               WHERE `ctl_num` = '{ctl_num}';""".
            format( ctl_num = ctl_num ) )

    def insert_field(
            self,
            ctl_num : str,
            tag     : str,
            seq     : int,
            code    : str,
            pos     : str,
            val     : str ):
        self.db.execute(
            """INSERT INTO MARC_fields (
                 `ctl_num`,
                 `tag`,
                 `seq`,
                 `code`,
                 `pos`,
                 `val`
               ) VALUES (
                 '{ctl_num}',
                 '{tag}',
                  {seq},
                 '{code}',
                 '{pos}',
                 '{val}'
               );""".
            format( ctl_num = ctl_num,
                    tag     = tag,
                    seq     = seq,
                    code    = code,
                    pos     = pos,
                    val     = esc( val ) ) )

    def update_field(
            self,
            ctl_num : str,
            tag     : str,
            seq     : int,
            code    : str,
            pos     : str,
            val     : str ):
        self.db.execute(
            """UPDATE MARC_fields
               SET `val` = '{val}'
               WHERE     `ctl_num` = '{ctl_num}'
                     AND `tag`  = '{tag}'
                     AND  seq   = {seq}
                     AND `code` = '{code}'
                     AND `pos`  = '{pos}';""".
            format( ctl_num = ctl_num,
                    tag     = tag,
                    seq     = seq,
                    code    = code,
                    pos     = pos,
                    val     = esc( val ) ) )

    def delete_field(
            self,
            ctl_num : str,
            tag     : str,
            seq     : int,
            code    : str,
            pos     : str ):
        self.db.execute(
            """DELETE FROM MARC_fields
               WHERE     `ctl_num` = '{ctl_num}'
                     AND `tag`  = '{tag}'
                     AND  seq   =  {seq}
                     AND `code` = '{code}'
                     AND `pos`  = '{pos}';""".
            format( ctl_num = ctl_num,
                    tag     = tag,
                    seq     = seq,
                    code    = code,
                    pos     = pos ) )

    def delete_all_fields( self, ctl_num: str ):
        self.db.execute(
            """DELETE FROM MARC_fields
               WHERE `ctl_num` = '{ctl_num}';""".
            format( ctl_num = ctl_num ) )


    # XXX Do this and the next two functions via an iterator because
    # these lists could be very large.
    def get_all_titles( self ) -> list:
        return self.db.row_array(
            """SELECT ctl_num, val
               FROM MARC_fields
               WHERE     tag  = '245'
                     AND code = 'a' """ )

    def get_all_subjects( self ) -> list:
        return self.db.row_array(
            """SELECT ctl_num, code, val
               FROM MARC_fields
               WHERE tag = '650' """ )

    def get_all_authorg36s( self ) -> list:
        return self.db.row_array(
            """SELECT ctl_num, tag, val
               FROM MARC_fields
               WHERE     tag LIKE '1%'
                     AND code =   'a' """ )


    def clear_keywords( self ):
        self.db.execute( 'DELETE FROM bib_keywords' )


    def match_keywords(
            self,
            key_list       : list,
            namespace_list : list,
            limit          : int )      -> list:
        limit_phrase = ''
        if limit > 0: limit_phrase = ' LIMIT {}'.format( limit )
        namespace_phrase = ''
        if len( namespace_list ) > 0:
            namespace_phrase = ' AND namespace IN ( {} )'.format(
                ','.join( map( lambda x: "'" + x + "'", namespace_list ) )
                )
        key_phrase = ' WHERE keyword IN ( {} )'.format(
            ','.join( map( lambda x: "'" + x + "'", key_list ) )
            )
        SQL ="""
          SELECT
            ctl_num,
            COUNT(*) AS count
          FROM
            bib_keywords
          {key_phrase}
          {namespace_phrase}
          GROUP BY
            ctl_num
          ORDER BY count DESC
          {limit_phrase};""".format(
            key_phrase        = key_phrase,
            namespace_phrase  = domain_phrase,
            limit_phrase      = limit_phrase )

        return [ tuple( row ) for row in self.db.row_array( SQL ) ]
