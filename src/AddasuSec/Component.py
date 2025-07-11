""""
Component.py

Defines the central concept of a component. In this model, the unit of separation is
an object with explicitly labeled interfaces and receptacles—i.e., the dependencies 
are defined by the component developer. Connections are then explicitly established 
between component interfaces and receptacles.

Author: Paul Grace  
License: MIT
"""

from AddasuSec.Receptacle import Receptacle
import inspect

def data_storage_method(func):
    """
    Decorator that marks a function as a data storage method.

    Args:
        func (callable): The function to mark.

    Returns:
        callable: The same function with an added attribute.
    """
    func.is_data_storage = True
    return func

def stakeholder_io_method(func):
    """
    Decorator that marks a function as a data input/output method.

    Args:
        func (callable): The function to mark.

    Returns:
        callable: The same function with an added attribute.
    """
    func.is_data_storage = True
    return func

class Component():
    """
    Represents a software component with explicitly defined dependencies (receptacles).
    Components can dynamically connect to other components through labeled interfaces.
    """

    def __init__(self, receptacle_list):
        self.receptacles = {}
        self.secure = False
        """
        Initialize the component with a list of receptacle types.

        Args:
            receptacle_list (list): List of receptacle types (strings) to initialize.
        """
        for item in receptacle_list:
            rcp = Receptacle(item)
            self.receptacles[item] = rcp

    def call_with_token(self, func, token, *args, **kwargs):
        print(f"Calling {func.__name__} with token: {token}")
        return func(token, *args, **kwargs)
    
    def receptacle_with_token(self, func, *args, **kwargs):
        stack = inspect.stack()
        previous_frame = stack[2].frame
        # Get local variables (including parameters) from that frame
        prev_args = previous_frame.f_locals
        print("Previous call's arguments:", prev_args)
    
        return func(prev_args['req'], *args, **kwargs)

    def getReceptacle(self, r_type):
        """
        Get the connected component instance for a given receptacle type.

        Args:
            r_type (str): The name of the receptacle.

        Returns:
            object: The connected component instance, or None if not connected.
        """
        rp = self.receptacles.get(r_type)
        return rp._Comp

    def setWrapper(self, c_inst):
        """
        Set a wrapper object for the component. This is used to wrap a plain component
        with the capabilities of a distributed component i.e. the interfaces become Web
        interfaces, and the receptacles become remote calls.

        Args:
            c_inst (object): The wrapper instance.
        """
        self.wrapper = c_inst

    def getWrapper(self):
        """
        Get the currently assigned wrapper instance.

        Returns:
            object: The wrapper object.
        """
        return self.wrapper

    def connect(self, component, intf):
        """
        Connect another component to one of this component's receptacles.

        Args:
            component (Component): The component to connect.
            intf (str): The interface/receptacle name.

        Returns:
            bool: True if connected successfully, False otherwise.
        """
        try:
            return self.receptacles.get(intf).connect(component, intf)
        except ValueError:
            return False

    def disconnect(self, intf):
        """
        Disconnect a component from one of this component's receptacles.

        Args:
            intf (str): The interface/receptacle name.

        Returns:
            bool: True if disconnected successfully, False otherwise.
        """
        try:
            return self.receptacles.get(intf).disconnect()
        except ValueError:
            return False

    def setSecure(self, value):
        self.secure = value
    
    def start(self):
        """
        Start the component. This is a stub meant to be overridden.

        Args:
            param (any): Parameter used during startup.

        Returns:
            bool: True if started successfully.
        """
        return True

    def stop(self):
        """
        Stop the component. This is a stub meant to be overridden.

        Returns:
            bool: True if stopped successfully.
        """
        return True
        