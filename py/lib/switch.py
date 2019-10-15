#!/usr/bin/env python3

class switch ( object ):
    """
    Pseudo-class to implement the switch/case language construct.

    from switch import switch

    for case in switch( value ):
        if case( 'foo' ):
            do_stuff()
            break
        if case( 'bar' ):
            do_something_else()
            break
        if case( 'baz', 'flarp' ):
            do_yet_another_thing()
            break
        if case():
            do_default_thing()
            break
    """

    def __init__( self, value ):
        self.value = value
        self.fall = False


    def __iter__( self ):
        """ Return the match method once, then stop """
        yield self.match
        raise StopIteration


    def match( self, *args ):
        """Determine whether to enter a case suite.  <args> is a list of selector values."""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False
