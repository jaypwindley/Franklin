#!/usr/bin/env python

#-----------------------------------------------------------------------
# Pseudo-class to implement the switch/case language construct.
#
#    from switch import switch
#
#    for case in switch( value ):
#        if case( 'foo' ):
#            do_stuff()
#            break
#        if case( 'bar' ):
#            do_something_else()
#            break
#        if case( 'baz', 'flarp' ):
#            do_yet_another_thing()
#            break
#        if case():
#            do_default_thing()
#            break;
#
class switch ( object ):
    
    def __init__( self, value ):
        self.value = value
        self.fall = False

    #-------------------------------------------------------------------
    # Return the match method once, then stop
    #
    def __iter__( self ):
        yield self.match
        raise StopIteration

    #-------------------------------------------------------------------
    # Determine whether to enter a case suite.  <args> is a list of
    # selector values.
    #
    def match( self, *args ):
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False
