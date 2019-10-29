#!/usr/bin/env python3
#-------------------------------------------------------------------------------
#  File:              TAG( MARC.py )
#  Description:       MARC 21 tags and records
#  Author:            Jay Windley <jwindley>
#  Created:           Thu May  2 13:01:34 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
#-------------------------------------------------------------------------------
"""MARC 21 tags and records"""

from datetime import datetime
import re
import hashlib

class fieldlist( list ):
    """List of fields in MARC 21 tag."""

    # MARC_record may occasionally override this.
    fld_delim = '|'

    def __init__( self ):
        self.fields = []


    def __len__( self ):
        """Override len() function to return the length of the included subfield list.

        """
        return len( self.fields )


    def __getitem__( self, code ):
        """Override subscription operator.  Find the first occurrence of <code> and return its associated
        value.

        """
        val = None
        for f in self.fields:
            if f[ 0 ] == code:
                val = f[ 1 ]
                break
        if val is None:
            raise KeyError( "subfield code '%s' not in '%s'"
                            % ( code, self.__str__() ) )
        return val


    def __setitem__( self, code, val ):
        """Find first instance of <code> and set it to val, which obviously isn't likely to do the right
        thing if there is more than one occurrence.  Otherwise append a new value onto it, which
        isn't likely to do the right thing either since tags have imposed order.

        """
        for i in range( len( self.fields ) ):
            if self.fields[ i ][ 0 ] == code:
                self.fields[ i ][ 1 ] = val
                return
        self.fields.append( code, val )


    class iterator():
        def __init__( self, fields ):
            self.fields = fields
            self.pos = 0
        def next( self ):
            """Returns the tuple ( <code>, <val> ) in sequence."""
            try:
                val = self.fields[ self.pos ]
                self.pos += 1
            except IndexError:
                raise StopIteration
            return val
        def __iter__( self ): return self;

    def __iter__( self ): return self.iterator( self.fields )


    def getall( self, code ):
        """Get all instances of a subfield code in order, as an ordered list of values."""
        matches = [ f[1] for f in self.fields if f[0] == code ]
        return matches


    def __str__( self ):
        """Return the canonical string representation of the field list."""
        return ''.join(
            [ self.fld_delim + f[0] + f[1].encode( 'utf-8' )
              for f in self.fields ]
            ).strip()


    def append( self, code, val ):
        """Append the subfield <code> and <val> to the present list."""
        self.fields.append( ( code, val ) )


    def join( self, sep = ' ', fields = [] ):
        """Return a string composed of subfield code values in <fields> (defaults to all codes in the tag)
        joined by <sep>.  Undefined subfield codes are ignored.  Returns the empty string if no
        subfields in <fields> (either default or explicit) are defined.

        """
        # if no subfield codes specified, construct a list of all
        # subfield codes.
        #
        if len( fields ) == 0:
            fields = [ sf[ 0 ] for sf in self.fields ]

        # Join values for all codes in the field list.
        #
        vals = []
        for code in fields:
            try: vals.append( self[ code ] )
            except KeyError: continue
        if len( vals ) > 0:
            return sep.join( vals )
        else:
            return ''



class tag( object ):
    """MARC 21 numbered tag"""

    def __init__( self,
                  tag = '000',
                  ind = '  ',
                  seq = 1,
                  str = '' ):

        self.tag         = tag    # 3-digit MARC tag
        self.seq         = seq    # position, for duplicate tags
        self.ind         = ind    # 2-char MARC indicator group
        self.fields      = fieldlist()

        # This overrides the individual args.
        if str is not '':
            self.parse_canonical_string( str )


    def join( self, sep = ' ', fields = [] ):
        """Return the value of the tag as a string, separated by <sep> as in classical join().  If a tag
        has more than one of the same subfield, all matching subfields are included in order.

        """
        return self.fields.join( sep, fields )


    def parse_canonical_string( self, s ):
        """Take string <s> as a canonical line-oriented representation of the MARC tag, where the line is
        fixed-field as

            TTT_II_|xAAAAAAAAAAA

        where TTT is the three-character, zero-padded tag number, II is the two-character,
        space-padded indidcators, | is the ostensible subfield delimiter, and x is the subfield code
        letter.

        Any text following the subfield code letter is part of the subfield value.  Assign tag,
        indicator, and fields as appropriate.

        """
        self.tag   = s[:3]
        self.ind   = s[4:6]

        values     = s[7:].rstrip()

        # Discover the delimiter.
        fieldlist.fld_delim = values[0]

        # Split on the delimiter, keeping in mind that the lead
        # character is the delimiter so the first split string will be
        # empty.  The first character of each split-out string will be
        # the subfield code.
        #
        subfields = values.split( fieldlist.fld_delim )
        for f in subfields[1:]:
            self.fields.append( f[0], f[1:] )


    def ord( self ):
        """Return a number expressing the unique position of this tag in the ordered sequence of tags in
        the record.

        """
        return int( self.tag + str( self.seq ) )


    def __str__( self ):
        """The string representation is the canonical MARC one-line representation of the tag.  See
        parse_canonical_string() for the details of the format.

        """
        return "%03s %02s %s" % (
            self.tag[0:3],
            self.ind[0:2],
            self.fields
            )

    def __iter__( self ): return self.fields.__iter__()




class record( object ):

    # Normally defers to MARC_tag.fld_delim but for output's sake etc. this takes precedence.
    #
    fld_delim = '|'

    def __init__( self, data = '' ):
        """If s is non-empty, it is assumed to be a canonical string representation of the record: tags are
        separated by the newline and LDR is the first tag, the MARC 21 leader.

        """
        self.leader     = '';   # MARC 21 leader
        self.ctl_fields = {}    # Control fields, 00X tags
        self.tags       = []    # list of MARC_tag objects
        self.seqs       = {}    # tag-indexed sequence counters

        if data != '':
            self.parse_canonical_string( data )


    def ctl_num( self ):
        """Return the record control number"""
        #   XXX: technically the control number namespace should be
        #        given in 003, but we cheat here and pull it from 040a
        #        because 003 isn't always there.
        return self.find( '040' ).fields['a'] + self.ctl_fields['001']


    def tl_deref( self, specs ):
        """Dereference the given tag list and return the joined string expressing it, or the empty string
        if none of the tags match.

        """
        s = ''
        for spec in specs:
            tag, fields = self.split_spec( spec )
            t = self.find( tag )
            if t is not None:
                return t.join( fields = fields )
        return s


    def split_spec( self, spec ):
        """For the given spec string, return the tag and a field list."""
        fields = []
        map( fields.extend, spec[3:] )
        return spec[:3], fields


    def cite( self ):
        """Return the MLA format citation string for this work."""
        return "%s %s. (%s)." % ( self.author(),
                                  self.title(),
                                  self.imprint() )


    def update_timestamp( self ):
        """Update the 005 control field (Date and Time of Last Transaction) with the current date and time.

        """
        self.ctl_fields[ '005' ] = datetime.now().strftime(
            '%Y%m%d%H%M%S'
            ) + '.0'

    def parse_canonical_string( self, s ):
        """The canonical string representation is one tag per line, with the leader as the first line.

        """
        lines = s.split( "\n" )
        if lines is None:
            return

        for line in lines:

            # Initialize sequence number if necessary.
            try:
                self.seqs[ line[:3] ] += 1
            except KeyError:
                self.seqs[ line[:3] ] = 1
            seq = self.seqs[ line[:3] ]

            # Leader
            if line[:3] == 'LDR':
                self.leader = line[7:].rstrip()
                continue

            # Control field
            if line[:2] == '00':
                self.ctl_fields[ line[:3] ] = line[7:].rstrip()
                continue

            # Regular tag
            self.tags.append( tag( str = line, seq = seq ) )


    def find( self, key, seq = 1 ):
        """Find the seq'th occurrence of tag <key> in the record and return its tag object.  Returns None
        if no such tag is in the record.

        """
        for t in self.tags:
            if t.tag == key and t.seq == seq:
                return t
        return None


    def filter( self, key ):
        """Find all the occurrences of tag <key> in the record and return a list of the associated tag
        objects.  Returns empty list if no such tag(s) are in the record.

        """
        results = []
        for t in self.tags:
            if t.tag == key:
                results.append( t )
        return results


    def strip_900s( self ):
        """Remove all 9xx tags.  These are internal Library of Congress tags. """
        T900_regex = re.compile( '^9[\digit]{2}$' )
        for t in self.tags:
            if T900_regex.match( t.tag ):
                self.tags.remove( t )


    def __str__( self ):
        """String representation is the canonical string representation of each tag in ordinal value.  The
        MARC leader is given the LDR tag.  Coerces the tag delimiter to be the record-scoped field
        delimiter.  Individual tags are separated by the newline.

        """
        tag.fld_delim = MARC_record.fld_delim
        s = 'LDR    ' + self.leader + "\n"
        for f in sorted( self.ctl_fields.keys() ):
            s += "%03s    %s\n" % ( f, self.ctl_fields[ f ] )
        for t in self.tags:
            s += t.__str__() + "\n"
        return s.rstrip()


    def digest( self ) -> str:
        return hashlib.md5( self.__str__() ).hexdigest()


    class iterator():
        """Iterate over tags (but not control fields).  State is maintained by a list of indices into
        self.tags, presented in tag-sorted order.  The local index is an index into that list of
        indices.

        """
        def __init__( self, rec ):
            self.rec = rec
            self.i   = 0

            #
            # Yes, I'm going to hell for this.  This is a list of
            # indices. It starts as a simple range over all the indices,
            # list-comprehensively, then sorted according to the tag
            # values combined with sequence numbers as in TTTS.
            #

            self.indices = sorted(
                [ i for i in xrange( len( self.rec.tags ) ) ],
                key = lambda i: int(
                    self.rec.tags[i].tag + '{:d}'.format(
                        self.rec.tags[i].seq
                        )
                    )
                )

        def next( self ):
            try:
                # Double-dereference the tags
                t = self.rec.tags[ self.indices[ self.i ] ]
                self.i += 1
            except IndexError:
                raise StopIteration
            return t
        def __iter__( self ): return self
    def __iter__( self ): return self.iterator( self )
