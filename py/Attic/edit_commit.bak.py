



    


########################################################################
#
#   Editable MARC 21 record
#
#
#
class MARC_edit_record( MARC_record ):

    def __init__( self, data = '' ):
        raise TypeError( 'MARC_edit_record is presently broken' )
        MARC_record.__init__( self, data )

    def __del__( self ):
        if False:
            raise UserWarning


    #-------------------------------------------------------------------
    # Return a map of differences between this object and a reference
    # object.  Keys to the map are the ordinal tag number (tag plus
    # sequence), where 'LDR' stands for the MARC leader.  Map values
    # are:
    #
    #  new        New tag in this record, not found in the reference.
    #
    #  deleted    Deleted from this record, but present in the
    #             reference.
    #
    #  updated    Present in both, but content differs in this record
    #             from the reference.  Only this value is allowed
    #             for 'LDR'
    #
    def diff( self, ref ):
        map = {}

        # Traverse current object to detect new and updated tags.
        for tag in self.sum_tags.keys():
            try:
                if ref.sum_tags[ tag ] != self.sum_tags[ tag ]:
                    map[ tag ] = 'updated'
            except KeyError:
                map[ tag ] = 'new'

        # Then traverse the reference object to detect deleted tags.
        for tag in ref.sum_tags.keys():
            try:
                if ref.sum_tags[ tag ] == self.sum_tags[ tag ]:
                    pass
            except KeyError:
                map[ tag ] = 'deleted'

        return map

    #-------------------------------------------------------------------
    # Return an editable version of the MARC record associated with
    # the given control number.  Locks the associated record in the
    # data store to prevent other updates.  Returns None if no such
    # record is found.
    #
    def edit( self, ctl_num ):
        rec = MARC_edit_record()        
        rec.leader = self.get_leader( ctl_num )
        if rec.leader is None: return None
        self.build_record( rec, ctl_num )
        rec.sums.sum( rec )
        return rec

    #-------------------------------------------------------------------
    # Commit an editable MARC record to the data store.
    #
    def edit_commit( self, rec ):

        # Check whether this is an editable record.
        if not isinstance( rec, MARC_edit_record ):
            raise TypeError

        # Compute new checksums and see whether anything has changed.    
        new_sums = MARC_edit_sums( rec )
        if new_sums.matches( rec.sums ): return

        # If record changed, update the modification time and
        # recompute the new checksums (to pick up change to mod time).
        #
        rec.update_timestamp()
        new_sums.sum( rec )

        # Determine what changed.
        edit_map = new_sums.diff( rec.sums )
        print edit_map

        for k in edit_map:

            # Leader.  Only update is allowed.
            if k == 'LDR':
                if edit_map[ k ] != 'updated':
                    raise ValueError
                self.update_leader( rec, rec.leader )
                continue

            # Control fields.  No indicators or sequences.
            if k[:2] == '00':
                self.edit_commit_control_field( edit_map[ k ], rec, k[:3] )
                continue

            # Tags.
            for case in switch( edit_map[ k ] ):
                tag  =      k[:3]
                seq  = int( k[3:4] )
                code =      k[4:5]

                # Indicators
                if code == '_':
                    self.edit_commit_indicators( edit_map[ k ], rec, tag, seq )
                    continue

                # Regular tag field
                self.edit_commit_field( edit_map[ k ], rec, tag, seq, code )

        self.commit()

        # Update the checksums.
        rec.sums = new_sums


    #-------------------------------------------------------------------
    # Commit a control field <tag> in <rec> to the data store, in the
    # mode commanded by <cmd>, which is one of the values of the
    # edit_map in data_bib.edit_commit() above.
    #
    def edit_commit_control_field( self, cmd, rec, tag ):
        for case in switch( cmd ):

            if case( 'deleted' ):
                self.delete_control_field( rec,ctl_num(), tag )
                break
            
            if case( 'updated' ):
                self.update_control_field( rec.ctl_num(),
                                           tag,
                                           rec.ctl_fields[ tag ] )
                break

            if case( 'new' ):
                self.insert_control_field( rec.ctl_num(),
                                           tag,
                                           rec.ctl_fields[ tag ] )
                break

            if case():
                raise ValueError


    #-------------------------------------------------------------------
    # Commit the indicators of <tag> <seq> in <rec> to the data store,
    # according to the <cmd> from edit_map in data_bib.edit_commit()
    # above.
    #
    def edit_commit_indicators( self, cmd, rec, tag, seq ):

        for case in switch( cmd ):
            
            t = rec.find( tag, seq )

            if case( 'deleted' ):
                self.delete_indicators( rec.ctl_num(), tag, seq )
                break;

            if case( 'updated' ):
                # If the new indicator is the default, then
                # just delete the indicator row.
                #
                if t is None: raise KeyError
                if t.ind == '  ':
                    self.delete_indicators( rec.ctl_num(), tag, seq )
                else:
                    self.update_indicators( rec.ctl_num(), tag, seq, t.ind )
                break

            if case( 'new' ):
                if t is None: raise KeyError
                self.insert_indicators( rec.ctl_num(),
                                        tag,
                                        seq,
                                        t.ind )
                break

            if case():
                raise ValueError


    #-------------------------------------------------------------------
    # Commit a subfield <tag> <seq> <code> <pos> in <rec> to the data
    # store, according to the <cmd> from edit_map above.
    #
    def edit_commit_field( self, cmd, rec, tag, seq, code, pos ):

        for case in switch( cmd ):

            t = rec.find( tag, seq )

            if case( 'deleted' ):
                self.delete_field( rec.ctl_num(), tag, seq, code, pos )
                break
            
            if case( 'updated' ):
                if t is None: raise ValueError
                self.update_field( rec.ctl_num(),
                                   tag,
                                   seq,
                                   t.fields[ pos ][ 0 ],
                                   pos,
                                   t.fields[ pos ][ 1 ] )
                break

            if case( 'new' ):
                if t is None: raise ValueError
                self.insert_field( rec.ctl_num(), tag, seq, code, pos, t.fields[ code ] )
                break;

            if case():
                raise ValueError
