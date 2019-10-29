#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              TAG( MARC_Z392.py )
#  Description:       MARC 21 encoding in ANSI Z39.2
#  Author:            Jay Windley <jwindley>
#  Created:           Thu May  2 13:01:34 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""Parase and/or render MARC records in ANSI Z39.2 format

   The ANSI Z39.2 protocol encodes tagged data with fixed and optional elements.  Each tag features
   a number of indicators and sub-encoded values.  MARC 21 is an implementation of the Z39.2 format
   with at most 2 single-digit indicators and subfield codes composed of a sentinel byte followed by
   a sequence character.

   A Z39.2 datagram has a fixed-length leader, a dictionary mapping tag names (3-digit numeric
   strings) to offsets and data lengths in the data segment, and then the data segment itself.

"""

import base64
import MARC

FT = '\x1E'        # field terminator   : after each tag data sequence
US = '\x1F'        # unit separator     : between tag subfields
RT = '\x1D'        # record terminator  : after the record


def parse_str( s: str ) -> MARC.record:
    """Parse <s> as a Z39.2 wire protocol datagram and return the equivalent MARC.record.  Returns None
    if an error occurs.

    """
    if len( s ) < 24: return None
    rec = MARC.record()
    rec.leader = s[:24]

    #-----------------------------------------------------------------
    # Parse the directory segment, returning a list of dictionaries
    # with the keys
    #
    #   tag:  the tag name
    #   len:  length of the segment data, including the terminator
    #   addr: offset from the beginning of the data segment.
    #
    # Argument <s> is the Z39.2 string with the leader removed
    #
    def parse_directory( self, s ) -> list:
        dir = []

        # If any of the slicing goes bad during the parsing, return what we have.
        #
        try:

            # Z39.2 specifies a 3-digit tag.  But the directory entry field widths are specified in
            # Leader/20 and Leader/21.  For MARC 21 these are "hard wired" to 4-digit lengths and
            # 5-digit addresses.
            #
            while s[0] != FT:
                t = s[0:3]               # 3-digit tag
                l = int( s[3:7]  )       # 4-digit length
                a = int( s[7:12] )       # 5-digit address

                # Save the directory entry and strip 12 characters from the front of the data
                # string.
                #
                dir.append( { 'tag':t, 'len':l, 'addr':a } );
                s = s[12:]

        except IndexError:
            pass
        return dir


    # Get the directory.
    dir = parse_directory( s[24:] )
    if len( dir ) == 0: return None

    #-----------------------------------------------------------------
    # Use the directory to parse the data segment.
    #
    #   s        The data segment -- the Z39.2 string with the 24
    #            characters of the leader and the directory (with its
    #            field terminator) removed
    #
    #   dir      Representation of the directory as produced by
    #            parse_directory
    #
    def parse_data( s: str, dir: list ):
        for d in dir:
            try:

                # Slice the data based on the directory entry.
                data = s[ d['addr'] : d['addr'] + d['len'] - 1 ]

                # Control fields don't get further parsed.
                if d['tag'][0:2] == '00':
                    rec.ctl_fields[ d['tag'] ] = data
                    continue

                # Make a tag and store the tag name, indicator, and
                # subfields
                #
                else:
                    t = MARC.tag()
                    t.tag = d['tag']
                    t.ind = data[0:2]

                    # Split the fields by the unit separator.  First
                    # character of each list element is the subfield
                    # code.
                    #
                    fields = data[3:].split( US )
                    for f in fields:
                        t.fields.append( f[0], f[1:] )
                    rec.tags.append( t )

            except:
                pass


    # Find the field terminator after the directory and parse the rest of it as tag data, accordgin
    # to the directory.
    #
    base_idx = s.index( FT )
    parse_data( rec, s[base_idx + 1:], dir )

    return rec


def render( rec: MARC.record, base_64 = False ) -> str:
    """Return a string containing the record in Z39.2 format.  Optionally encode it in base-64."""
    data = ''
    dir  = ''

    #-----------------------------------------------------------------
    # Traverse the MARC record and accumulate the data segment and
    # directory segment simultaneously.  The single traversal makes
    # the accumulation deterministic.
    #
    def traverse( rec: MARC.record ):
        base_addr = 0

        # Add control fields.  These don't have subfield codes.
        for k in sorted( rec.ctl_fields.keys() ):
            dir += "%03s" % k          # tag name, no indicators

            val = rec.ctl_fields[ k ] + FT
            data += val

            length = len( val )
            dir += "%04d" % length    # add length
            dir += "%05d" % base_addr # add base address
            base_addr += length

        # Add data tags to the directory.
        for t in rec:
            dir += "%03s" % t.tag      # tag name
            field_data = t.ind[:2]     # indicators

            # Add each field with its code.
            for f in t.fields:
                field_data += "%c%c%s" % ( US, f[ 0 ], f[ 1 ] )

            # Terminate the tag.
            field_data += FT
            data += field_data

            length = len( field_data )
            dir += "%04d" % length     # add length to directory
            dir += "%05d" % base_addr  # add base address to directory
            base_addr += length

        # Terminate the directory.
        self.dir += FT

    traverse( rec )
    s = rec.leader + dir + data + RT
    if base_64:
        return base64.b64encode( s )
    else:
        return s
