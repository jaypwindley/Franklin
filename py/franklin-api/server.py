#!/usr/bin/env python3

from flask import Flask
import sys

sys.path.append( '../lib' )

import config

app = Flask( __name__ )

@app.route( '/', methods = [ 'GET', 'PATCH' ] )
def test():
    return "Hi there\n"

if __name__ == "__main__":
    app.run( host = '0.0.0.0', port = config.REST[ 'port' ] )
