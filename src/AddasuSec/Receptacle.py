""""
Receptacle.py

Defines the central concept of a component. In this model, the unit of separation is
an object with explicitly labeled interfaces and receptacles—i.e., the dependencies 
are defined by the component developer. Connections are then explicitly established 
between component interfaces and receptacles.

Author: Paul Grace  
License: MIT
"""
import inspect

class Receptacle:
    """
    Receptacle class representing a container for connecting components and storing metadata.

    Attributes:
        iid (str): The interface identifier that the receptacle will accept.
        _Comp (Any): The connected component (sink object).
        m_connID (int): Connection identifier used for validation during disconnection.
        meta_Data (dict[str, Any]): Dictionary to store arbitrary key-value metadata.
    """

    def __init__(self, id: str) -> None:
        """
        Initialize the Receptacle with a specific interface ID.

        Args:
            id (str): The expected interface ID for connections.
        """
        self.iid: str = id
        self._Comp = None
        self.meta_Data: dict[str, any] = {}

    def connect(self, pIUnkSink: object, riid: str) -> bool:
        """
        Connect a component if the interface ID matches.

        Args:
            pIUnkSink (object): The component to connect.
            riid (str): The interface ID of the component attempting to connect.

        Returns:
            bool: True if the component is successfully connected; False otherwise.
        """
        if riid != self.iid:
            return False
        self._Comp = pIUnkSink
        return True

    def disconnect(self) -> bool:
        """
        Disconnect the component if the connection ID matches.

        Args:
            id (int): The connection ID to validate against the current connection.

        Returns:
            bool: True if the component is successfully disconnected; False otherwise.
        """
        if self._Comp != None:
            self._Comp = None
            return True
        return False

    def putData(self, name: str, value: object) -> None:
        """
        Store a key-value pair in the metadata dictionary.

        Args:
            name (str): The key under which to store the value.
            value (object): The value to store.
        """
        self.meta_Data[name] = value

    def getValue(self, name: str) -> object:
        """
        Retrieve a value by key from the metadata dictionary.

        Args:
            name (str): The key whose value to retrieve.

        Returns:
            object: The stored value, or None if the key does not exist.
        """
        return self.meta_Data.get(name)

    def getValues(self) -> list[object]:
        """
        Retrieve all values stored in the metadata dictionary.

        Returns:
            list[object]: A list of all stored metadata values.
        """
        return list(self.meta_Data.values())
