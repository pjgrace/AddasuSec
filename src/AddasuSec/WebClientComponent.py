"""
WebClientComponent Module

This module defines the WebClientComponent class, which acts as a wrapper around a component
that uses WebReceptacle-based receptacles. It enables dynamic method invocation, component
connection management, and token-based function execution. It also defines a decorator to
mark methods as data storage operations.
"""

import AddasuSec.WebReceptacle

def data_storage_method(func):
    """
    Decorator to mark a method as a data storage method.

    Args:
        func (function): The function to be marked.

    Returns:
        function: The decorated function with an attribute flag.
    """
    func.is_data_storage = True
    return func

class WebClientComponent:
    """
    A wrapper component that manages receptacles and facilitates interactions
    such as connecting to other components and handling token-based function calls.
    """

    receptacles = {}

    def __init__(self, component):
        """
        Initialize the WebClientComponent with an inner component and convert its
        receptacles into WebReceptacle instances.

        Args:
            component (object): The inner component containing receptacles.
        """
        self.innerComponent = component
        for item in component.receptacles:
            rcp = AddasuSec.WebReceptacle.WebReceptacle(item)
            self.innerComponent.receptacles[item] = rcp

    def dynamic_call(self, name: str, *args, **kwargs):
        """
        Dynamically calls a method named 'get_<name>' if it exists.

        Args:
            name (str): Name suffix of the method to call.
            *args: Positional arguments to pass to the method.
            **kwargs: Keyword arguments to pass to the method.
        """
        method_name = f"get_{name}"
        if hasattr(self, method_name) and callable(getattr(self, method_name)):
            func = getattr(self, method_name)
            func(*args, **kwargs)

    def getReceptacle(self, r_type):
        """
        Retrieve the component connected to a receptacle of a given type.

        Args:
            r_type (str): The type of the receptacle.

        Returns:
            object: The connected component, or None if not found.
        """
        rp = self.receptacles.get(r_type)
        return rp._Comp if rp else None

    def call_with_token(self, func, token, *args, **kwargs):
        """
        Call a function with a token and additional arguments.

        Args:
            func (function): The function to call.
            token (str): Authentication token.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Any: The return value from the called function.
        """
        print(f"Calling {func.__name__} with token: {token}")
        return func(token, *args, **kwargs)

    def connect(self, component, intf, rt):
        """
        Connect a component to a specified interface and receptacle type.

        Args:
            component (object): The component to connect.
            intf (str): Interface name.
            rt (str): Receptacle type.

        Returns:
            bool: True if connected successfully, False otherwise.
        """
        try:
            return self.innerComponent.receptacles.get(intf).connect(component, intf, rt)
        except ValueError:
            return False

    def disconnect(self, intf):
        """
        Disconnect a component from a given interface.

        Args:
            intf (str): The interface name to disconnect.

        Returns:
            bool: True if disconnected successfully, False otherwise.
        """
        try:
            return self.innerComponent.receptacles.get(intf).disconnect(intf)
        except ValueError:
            return False

    def start(self, param):
        """
        Start the component. This method is a placeholder.

        Args:
            param (Any): Initialization parameter.

        Returns:
            bool: Always True for now.
        """
        return True

    def stop(self):
        """
        Stop the component. This method is a placeholder.

        Returns:
            bool: Always True for now.
        """
        return True
