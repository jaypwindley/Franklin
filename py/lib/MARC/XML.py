#!/usr/bin/env python
# -----------------------------------------------------------------------
#  File:              TAG( MARC_XML.py )
#  Description:       MARC XML parser and renderer
#  Author:            Jay Windley <jwindley>
#  Created:           Thu May  2 13:00:41 2013
#  Copyright:         (c) 2013 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------

import os
import sys
import xml.etree.ElementTree as ET

from MARC import MARC_tag, MARC_record
from MARC_bib import MARC_bib

#-----------------------------------------------------------------------
# A few decorators to properly qualify the element names in MARC-XML
# elements.
#
def tag( suffix ): return '{http://www.loc.gov/zing/srw/}' + suffix
def ns( suffix ):  return '{http://www.loc.gov/MARC21/slim}' + suffix


########################################################################
#
#  XML Parser
#
#  The parse_XXX() methods parse an XML file or a string,
#  respectively, in the MARC XML format.
#
# XXX should probably inherit from something basic
#
class MARC_XML_parser( object ):

    #-------------------------------------------------------------------
    # Parse <s> as XML and return the associated ElementTree, or None
    # on failure.
    #
    # XXX: should probably figure out how to merge with the file-based
    # function, since the distinction for this purpose is silly.
    #
    def parse_string( self, s ):
        tree = ET.fromstring( s )
        if tree is None:  return None
        return self.parse_tree( tree )

    #-------------------------------------------------------------------
    # Open the named file and attempt to parse its contents as XML.
    # Returns an ElementTruee on success and None on failure.
    #
    def parse_file( self, path ):
        tree = ET.parse( path )
        if tree is None: return None
        return self.parse_tree( tree.getroot() )



    #-------------------------------------------------------------------
    # Return a list of MARC record objects contained in the
    # ElementTree.  Ostensibly this should be only one, but LC queries
    # can return multiple hits.  Returns empty list if the file
    # contains no MARC records.
    #
    def parse_tree( self, root ):
        records = []
        
        if root is None: return records
        
        reclist = root.find( tag('records') )
        if reclist is None: return records

        for rec in reclist:
            records.append( self.parse_record( rec ) )
            
        return records


    #-------------------------------------------------------------------
    # Parse a single XML element representing a MARC21 record and
    # return a new MARC_record object embodying it.  Returns None on
    # error.
    #
    def parse_record( self, rec ):
        mrec = MARC_bib()

        # Not really accustomed to the MARC21 namespace prefixes, but
        # this is how it seems to be.
        #
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

                # Initialize or increment the sequence count for this
                # tag.
                #
                tag_name = f.attrib[ 'tag' ]
                try:
                    mrec.seqs[ tag_name ] += 1
                except KeyError:
                    mrec.seqs[ tag_name ] = 1

                # Tag, sequence, and indicators.
                mtag = MARC_tag( tag = tag_name,
                                 ind = f.attrib['ind1'] + f.attrib['ind2'],
                                 seq = mrec.seqs[ tag_name ] )

                # Subfields.
                for sf in f:
                    mtag.fields.append( sf.attrib['code'], sf.text )

                mrec.tags.append( mtag )
                
        return mrec
        

