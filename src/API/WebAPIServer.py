"""
API Server module

This module defines the Falcon web application and registers the main API routes
for managing components, including creation, deletion, connection, disconnection,
and starting components.

The server can be run standalone with the built-in WSGI server or deployed with
production WSGI servers such as Gunicorn or Waitress.
"""

import falcon
from wsgiref.simple_server import make_server

from API.WebAPI import (
    StartComponentResource,
    CreateComponentResource,
    DeleteComponentResource,
    ConnectResource,
    DisconnectResource
)

# Initialize Falcon application
app = falcon.App()

# Register API routes with corresponding resource handlers
app.add_route('/create', CreateComponentResource())
app.add_route('/delete', DeleteComponentResource())
app.add_route('/connect', ConnectResource())
app.add_route('/disconnect', DisconnectResource())
app.add_route('/start', StartComponentResource())


def main():
    """
    Starts the WSGI server on port 8654 and serves the Falcon app until terminated.
    """
    with make_server('', 8654, app) as httpd:
        print('Serving on port 8654...')
        httpd.serve_forever()


if __name__ == '__main__':
    main()
