#!/usr/bin/env python

from MARC import MARC_record, MARC_fieldlist

class MARC_bib( MARC_record ):

    # Field list specifications for high-level accessors.  First three
    # characters are the tag number.  Rest of the string is field
    # designators in order.  Specifications listed in decreasing order
    # of applicability.  After LoC FRBR Display Specification.
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

    def author( self ):     return self.tl_deref( self.tl_author  )
    def title( self ):      return self.tl_deref( self.tl_title   ).rstrip( '/ ' )
    def imprint( self ):    return self.tl_deref( self.tl_imprint ).rstrip( '.' )
