#!/usr/bin/env python3
# -----------------------------------------------------------------------
#  File:              bib.py
#  Description:       Bibliographic record, wrapper around MARC record
#  Author:            Jay Windley <jwindley>
#  Created:           Tue Oct 29 13:27:29 2019
#  Copyright:         (c) 2019 Jay Windley
#                     All rights reserved.
# -----------------------------------------------------------------------
"""Bibliographic record, wrapper around MARC record"""

from MARC import MARC

class bib( MARC.record ):

    # Field list specifications for high-level accessors.  First three characters are the tag
    # number.  Rest of the string is field designators in order.  Specifications listed in
    # decreasing order of applicability.  After LoC FRBR Display Specification.
    #
    tl_author  = [ '100abcd', '110abcd', '111acdnq', '700ad' ]
    tl_title   = [ '240adkmnpr', '243admnpr', '245agknp' ]
    tl_imprint = [ '260bcg' ]


    #----------------------------------------------------------------
    # Convience accessors and formatters.
    #
    #
    #   XXX: None returns generate exceptions when methods aren't
    #        defined over them.
    #
    def LC_call( self ):    return self.find( '050' ).join('')
    def Dewey_call( self ): return self.find( '082' ).join( '--dc', fields = ['a', '2'] )
    def ISBN( self ):       return self.find( '020' ).join( fields = ['a'] ).split()[0]

    def author( self ):     return self.tl_deref( bib.tl_author  )
    def title( self ):      return self.tl_deref( bib.tl_title   ).rstrip( '/ ' )
    def imprint( self ):    return self.tl_deref( bib.tl_imprint ).rstrip( '.' )

    def cite( self ):
        """Return the MLA format citation string for this work."""
        return "%s %s. (%s)." % ( self.author(),
                                  self.title(),
                                  self.imprint() )
