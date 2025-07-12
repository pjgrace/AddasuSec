"""
WebComponent Server Module

This module defines a WebComponent wrapper around an internal component, exposing its methods via Falcon HTTP routes.
It supports secure authentication through JWT, asynchronous method execution, and flexible parameter handling.

Classes:
    ServerThread: Threaded WSGI server for running Falcon apps.
    WebComponent: Main class to wrap components and expose methods as HTTP endpoints.

Author: Paul Grace

"""

import falcon
import inspect
import asyncio
import datetime
import uuid
import json
from AddasuSec import WebReceptacle
from Runtimes.Auth.JWTMiddleware import JWTAuthMiddleware
import threading
from waitress import serve
from wsgiref.simple_server import make_server
import requests
import time

class ServerThread(threading.Thread):
    """
    Threaded server for hosting a Falcon application.
    """
    def __init__(self, app, port):
        super().__init__()
        self.app = app
        self.port = port
        self.httpd = None

    def run(self):
        print(f"Serving on http://127.0.0.1:{self.port}")
        with make_server('', self.port, self.app) as self.httpd:
            self.httpd.serve_forever()

    def stop(self):
        if self.httpd:
            print("Shutting down server...")
            self.httpd.shutdown()
            try:
                requests.get(f'http://localhost:{self.port}/__shutdown__')
            except Exception:
                pass

class WebComponent:
    """
    A web wrapper that exposes an internal component's methods over HTTP using Falcon.
    Supports dynamic route management and optional JWT-based security.
    """

    innerComponent = None
    receptacles = {}

    def __init__(self, component, secure):
        """
        Initialize the WebComponent.

        Args:
            component (object): Component instance with callable methods.
            secure (bool): Enable JWT authentication if True.
        """
        self.innerComponent = component
        for item in component.receptacles:
            rcp = WebReceptacle.WebReceptacle(item)
            self.innerComponent.receptacles[item] = rcp

        self.dynamic_routes = {}
        self.app = falcon.App(middleware=[JWTAuthMiddleware()] if secure else [])

    def add_route(self, path, resource):
        """
        Add a new Falcon route.

        Args:
            path (str): Route path.
            resource (object): Falcon resource instance.
        """
        self.dynamic_routes[path] = resource
        self.app.add_route(path, resource)

    def remove_route(self, path):
        """
        Remove a route from the internal route map.

        Args:
            path (str): Route path to remove.
        """
        self.dynamic_routes.pop(path, None)

    def call_and_serialize(self, method, *args, **kwargs):
        """
        Call a method and serialize the result to JSON.

        Args:
            method (function): Callable method.

        Returns:
            str: JSON serialized result.
        """
        result = method(*args, **kwargs)
        return json.dumps(result)

    def startThreadedServer(self, port):
        """
        Start the Falcon app on a new thread.

        Args:
            port (int): Port number to run the server on.
        """
        self.port = port
        self.server = ServerThread(self.app, port)
        self.server.start()
        time.sleep(2)

    def stopThreadedServer(self):
        """
        Stop the running server and join the thread.
        """
        self.server.stop()
        self.server.join()
        print("Done.")

    def on_post(self, req, resp):
        """
        Handle POST request to dynamically invoke component methods.
        Automatically resolves arguments from query parameters.
        """
        print("USER FROM CONTEXT:", getattr(req.context, "user", None))
        nm = req.path.rpartition('/')[-1]
        methods = [attr for attr in dir(self.innerComponent)
                   if callable(getattr(self.innerComponent, attr)) and not attr.startswith("__")]
        print("Available methods:", methods)

        if nm in methods:
            method = getattr(self.innerComponent, nm)
            sig = inspect.signature(method)
            args = []

            for name, param in sig.parameters.items():
                annotation = param.annotation
                annotation_str = annotation if annotation != inspect._empty else str
                print(f"  {name}: {annotation_str}")
                args.append(self.get_typed_param(req, name, annotation_str))

            if inspect.iscoroutinefunction(method):
                result = asyncio.run(method(req, *args))
            else:
                try:
                    result = method(req, *args)
                except Exception:
                    result = method(*args)

            print(f"Result of calling {nm}: {result}")
            resp.media = {"result": result}
            resp.set_header('Powered-By', 'Falcon')
            resp.status = falcon.HTTP_200

        else:
            raise falcon.HTTPServiceUnavailable(
                title='Service Outage',
                description='The method called is not implemented on the component.',
                retry_after=30
            )

    def get_typed_param(self, req: falcon.Request, name: str, param_type: type):
        """
        Retrieve a typed parameter from a Falcon request.

        Args:
            req (falcon.Request): Incoming request.
            name (str): Parameter name.
            param_type (type): Expected type.

        Returns:
            Any: Typed parameter value.
        """
        type_method_map = {
            str: req.get_param,
            int: req.get_param_as_int,
            float: req.get_param_as_float,
            bool: req.get_param_as_bool
        }

        if param_type in type_method_map:
            value = type_method_map[param_type](name)
        else:
            raw = req.get_param(name)
            try:
                if param_type is datetime.date:
                    value = datetime.date.fromisoformat(raw)
                elif param_type is uuid.UUID:
                    value = uuid.UUID(raw)
                elif param_type is dict:
                    value = json.loads(raw)
                else:
                    raise TypeError(f"Unsupported type: {param_type.__name__}")
            except (ValueError, json.JSONDecodeError):
                raise TypeError(f"Could not convert parameter '{name}' to type: {param_type.__name__}")

        return value

    def connect(self, component, intf, rt):
        """
        Connect the internal component to another component via a receptacle.
        """
        try:
            return self.innerComponent.receptacles.get(intf).connect(component, intf, rt)
        except ValueError:
            return False

    def disconnect(self, component, intf, rt):
        """
        Disconnect the internal component from a receptacle.
        """
        try:
            return self.innerComponent.receptacles.get(intf).disconnect(intf)
        except ValueError:
            return False

    def start(self):
        """
        Start the component (stub).

        Returns:
            bool: True
        """
        return True

    def stop(self):
        """
        Stop the component (stub).

        Returns:
            bool: True
        """
        return True
