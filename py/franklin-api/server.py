#!/usr/bin/env python3

from flask import Flask
import sys

sys.path.append( '../lib' );
import license
import config

sys.path.append( './blueprints' )

app = Flask( __name__ )

# Discover and register the feature-specific blueprints.
for f in config.API[ 'features' ]:
    if license.is_valid( f ):
        bp = __import__( f + '.' + f, fromlist=[ f ] )
        app.register_blueprint( bp.responder )


if __name__ == "__main__":
    app.run( host = '0.0.0.0', port = config.REST[ 'port' ] )
