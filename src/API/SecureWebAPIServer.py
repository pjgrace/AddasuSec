"""
APIServer module

This module defines the APIServer class that sets up a Falcon-based HTTP API server 
with endpoints for component management (create, delete, connect, disconnect, start).

It includes middleware to log each incoming request along with authentication details 
extracted from OAuth Bearer tokens, logging client IP, port, HTTP method, response status, 
elapsed time, username, and user roles to a file.

Usage:
    Run this module directly to start the server on the specified host and port.

Example:
    $ python apiserver.py

Dependencies:
    - falcon
    - wsgiref (standard library)
    - API.WebAPI (application-specific resources)

Author: Paul Grace
"""

import falcon
from wsgiref.simple_server import make_server
import logging
import time
import jwt

from API.WebAPI import (
    StartComponentResource,
    CreateComponentResource,
    DeleteComponentResource,
    ConnectResource,
    DisconnectResource
)


class APIServer:
    """
    Falcon API Server for managing components with detailed logging and OAuth Bearer token authentication.
    """

    def __init__(self, host='0.0.0.0', port=8654, log_file='apiserver.log', jwt_secret='your_jwt_secret'):
        """
        Initialize the APIServer instance.

        Args:
            host (str): Host IP to bind the server to.
            port (int): Port number to listen on.
            log_file (str): Path to the log file.
            jwt_secret (str): Secret key for decoding JWT tokens.
        """
        self.host = host
        self.port = port
        self.jwt_secret = jwt_secret

        self.app = falcon.App(middleware=[self.LoggingMiddleware(self.jwt_secret, log_file)])

        self.app.add_route('/create', CreateComponentResource())
        self.app.add_route('/delete', DeleteComponentResource())
        self.app.add_route('/connect', ConnectResource())
        self.app.add_route('/disconnect', DisconnectResource())
        self.app.add_route('/start', StartComponentResource())

        self._setup_logging(log_file)

    def _setup_logging(self, log_file):
        """
        Configure logging to file.

        Args:
            log_file (str): Path to the log file.
        """
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    class LoggingMiddleware:
        """
        Falcon middleware to log requests including client IP, port, HTTP method, path, status,
        elapsed time, username, and roles extracted from OAuth Bearer tokens.
        """

        def __init__(self, jwt_secret, log_file):
            self.jwt_secret = jwt_secret
            self.logger = logging.getLogger(__name__)

        def process_request(self, req, resp):
            """
            Start timer at the beginning of the request.
            """
            req.context.start_time = time.time()

        def process_response(self, req, resp, resource, req_succeeded):
            """
            Log request and response details after processing.
            """
            elapsed_ms = (time.time() - getattr(req.context, 'start_time', time.time())) * 1000
            ip = req.remote_addr or 'unknown'
            port = req.access_route[-1].split(':')[1] if req.access_route else 'unknown'
            method = req.method
            path = req.path
            status = resp.status
            username = 'anonymous'
            roles = 'none'

            auth_header = req.get_header('Authorization')
            if auth_header and auth_header.lower().startswith('bearer '):
                token = auth_header[7:]
                try:
                    decoded = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
                    username = decoded.get('user', username)
                    roles = ','.join(decoded.get('roles', [])) if isinstance(decoded.get('roles'), list) else decoded.get('roles', roles)
                except jwt.PyJWTError:
                    # Invalid token, keep defaults
                    pass

            self.logger.info(
                f"{ip}:{port} {method} {path} {status} {elapsed_ms:.2f}ms user={username} roles={roles}"
            )

    def run(self):
        """
        Run the Falcon server using wsgiref.simple_server.
        """
        print(f"Starting API server on {self.host}:{self.port}...")
        with make_server(self.host, self.port, self.app) as httpd:
            print(f"Serving on http://{self.host}:{self.port}")
            httpd.serve_forever()


if __name__ == '__main__':
    server = APIServer()
    server.run()
