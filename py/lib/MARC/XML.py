#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              TAG( XML.py )
#  Description:       MARC XML parser and renderer
#  Author:            Jay Windley <jwindley>
#  Created:           Thu May  2 13:00:41 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""Parse and/or render MARC records to/from XML"""

import os
import sys
import xml.etree.ElementTree as ET

from MARC import MARC

# A few decorators to properly qualify the element names in MARC-XML elements.
def tag( suffix ): return '{http://www.loc.gov/zing/srw/}' + suffix
def ns( suffix ):  return '{http://www.loc.gov/MARC21/slim}' + suffix


def parse_tree( root: ET ) -> list:
    """Return a list of MARC record objects contained in the ElementTree <root>.  Ostensibly this should
    be only one, but this is meant for LC queries, and they can return multiple hits.  Returns empty
    list if the file contains no MARC records.

    """
    records = []

    if root is None: return records

    # Parse a single XML element representing an entire MARC21 record and return a new MARC.record
    # object embodying it.  Returns None on error.
    #
    def parse_record( rec: ET ) -> MARC.record:
        mrec = MARC.record()

        # Not really accustomed to the MARC21 namespace prefixes, but this is how it seems to be.
        data = rec.find( tag('recordData') ).find( ns('record') )
        if data is None: return mrec

        # Find the (hopefully single) leader element.
        mrec.leader = data.find( ns('leader') ).text

        # Find all the control (00x) fields.
        ctl_fields = data.findall( ns('controlfield') )
        if ctl_fields is not None:
            for f in ctl_fields:
                mrec.ctl_fields[ f.attrib['tag'] ] = f.text

        # Find all the data tags.
        data_fields = data.findall( ns('datafield') )
        if data_fields is not None:
            for f in data_fields:

                # Initialize or increment the sequence count for this tag.
                #
                tag_name = f.attrib[ 'tag' ]
                try:
                    mrec.seqs[ tag_name ] += 1
                except KeyError:
                    mrec.seqs[ tag_name ] = 1

                # Tag, sequence, and indicators.
                mtag = MARC.tag( tag = tag_name,
                                 ind = f.attrib['ind1'] + f.attrib['ind2'],
                                 seq = mrec.seqs[ tag_name ] )

                # Subfields.
                for sf in f:
                    mtag.fields.append( sf.attrib['code'], sf.text )

                mrec.tags.append( mtag )

        return mrec

    reclist = root.find( tag('records') )
    if reclist is None: return records

    for rec in reclist:
        records.append( parse_record( rec ) )

    return records


# @todo should probably figure out how to merge with the file-based function, since the distinction
# for this purpose is silly.
#
def parse_str( s: str ) -> list:
    """Parse <s> as XML and return the associated ElementTree, or None on failure."""

    tree = ET.fromstring( s )
    if tree is None:  return None
    return parse_tree( tree )


def parse_file( path: str ) -> list:
    """Open the named file and attempt to parse its contents as XML. Returns an ElementTruee on success
    and None on failure.

    """
    tree = ET.parse( path )
    if tree is None: return None
    return parse_tree( tree.getroot() )
