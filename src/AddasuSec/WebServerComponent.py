"""
WebServerComponent Module

This module defines a Falcon-based server component wrapper that allows dynamic
method invocation on inner components over HTTP.

Classes:
    WebServerComponent: A component that exposes functionality via Falcon API endpoints.

Author: Paul Grace
"""

from wsgiref.simple_server import make_server
import falcon
import inspect
import asyncio
import datetime
import uuid
import json
from AddasuSec.Receptacle import Receptacle


class WebServerComponent:
    """
    A wrapper class to expose an internal component's methods via Falcon HTTP routes.

    Attributes:
        innerComponent (Any): The wrapped component exposing methods over HTTP.
        receptacles (dict): Dictionary of receptacles.
        secure (bool): Indicates if the component is operating in secure mode.
    """

    innerComponent = None
    receptacles = {}
    secure = False

    def __init__(self, component):
        """
        Initialize the WebServerComponent with an inner component.

        Args:
            component (Any): The component instance to wrap.
        """
        self.innerComponent = component
        self.receptacles = component.receptacles

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """
        Handle POST requests and dynamically invoke inner component methods.

        Args:
            req (falcon.Request): The incoming request.
            resp (falcon.Response): The outgoing response.

        Raises:
            falcon.HTTPServiceUnavailable: If the method requested is not found.
        """
        print("USER FROM CONTEXT:", getattr(req.context, "user", None))
        method_name = req.path.rpartition('/')[-1]

        methods = [
            attr for attr in dir(self.innerComponent)
            if callable(getattr(self.innerComponent, attr)) and not attr.startswith("__")
        ]
        print("Available methods:", methods)

        if method_name in methods:
            method = getattr(self.innerComponent, method_name)
            sig = inspect.signature(method)
            args = []

            for name, param in sig.parameters.items():
                annotation = param.annotation
                annotation_str = annotation if annotation != inspect._empty else "No type annotation"
                print(f"  {name}: {annotation_str}")
                args.append(self.get_typed_param(req, name, annotation_str))

            try:
                if inspect.iscoroutinefunction(method):
                    result = asyncio.run(method(req, *args))
                else:
                    result = method(req, *args)
            except Exception:
                result = method(*args)

            print(f"Result of calling {method_name}: {result}")
        else:
            print(f"Method '{method_name}' not found.")
            raise falcon.HTTPServiceUnavailable(
                title='Service Outage',
                description='The requested method was not found.',
                retry_after=30
            )

        resp.media = {'result': result}
        resp.set_header('Powered-By', 'Falcon')
        resp.status = falcon.HTTP_200

    def get_typed_param(self, req: falcon.Request, name: str, param_type: type):
        """
        Retrieve and convert a typed parameter from a Falcon request.

        Args:
            req (falcon.Request): The incoming request.
            name (str): Parameter name.
            param_type (type): Expected Python type of the parameter.

        Returns:
            Any: Converted parameter value.

        Raises:
            TypeError: If the parameter cannot be converted or an unsupported type is given.
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
                raise TypeError(f"Unsupported type or malformed value for: {param_type.__name__}")

        return value

    def connect(self, component, intf: str) -> bool:
        """
        Connects another component to a specified receptacle.

        Args:
            component (Any): The component to connect.
            intf (str): Interface/receptacle name.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            return self.innerComponent.receptacles.get(intf).connect(component, intf)
        except ValueError:
            return False

    def disconnect(self, intf: str) -> bool:
        """
        Disconnect a component from one of this component's receptacles.

        Args:
            intf (str): The interface/receptacle name.

        Returns:
            bool: True if disconnected successfully, False otherwise.
        """
        try:
            return self.innerComponent.receptacles.get(intf).disconnect()
        except ValueError:
            return False

    def setSecure(self, value: bool) -> None:
        """
        Set the secure mode flag.

        Args:
            value (bool): True to enable secure mode, False otherwise.
        """
        self.secure = value
