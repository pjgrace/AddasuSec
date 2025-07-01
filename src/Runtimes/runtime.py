from Runtimes.ComponentRuntime import ComponentRuntime, PlainComponentException,\
    PlainConnectionException
from Runtimes.rpcRuntime import rpcRuntime
from Runtimes.clientRuntime import clientRuntime
from Runtimes.serverRuntime import serverRuntime
from AddasuSec.component import component

# Exception raised during creation and deletion of components.
class ComponentException(Exception):
    pass

# Exception raised during connection and disconnection of components.
class ConnectionException(Exception):
    pass

class runtime():
    
    def __init__(self, meta):
        self.meta = meta
        self.plainRuntime = ComponentRuntime(meta)
        self.webRuntime = rpcRuntime(meta)
        self.clientRuntime = clientRuntime(meta)
        self.serverRuntime = serverRuntime(meta)
        
     # CONNECT - Two Component in same address space.
    
    # This is the connect of two local address space components
    # The causal connection updates the global meta model with the
    # meta data
    def connect(self, type, component_src, component_intf, intf_type):
        match type:
            case "plain":
                try:
                    return self.plainRuntime.connect(component_src, component_intf, intf_type)
                except PlainConnectionException as e:
                    raise ConnectionException(e)
            case 'web':
                return self.webRuntime.connect(component_src, component_intf, intf_type)
            case 'web_client':
                return self.clientRuntime.connect(component_src, component_intf, intf_type)
            case 'web_server':
                return self.serverRuntime.connect(component_src, component_intf, intf_type)
            case _:
                raise ConnectionException("Incorrect runtimeType set, must be {plain, web, web_client, or web_server") 

    
    # DISCONNECT - Two Component in same address space
    def disconnect(self, type, component_src, component_intf, intf_type):
        match type:
            case "plain":
                return self.plainRuntime.disconnect(component_src, component_intf, intf_type)
            case 'web':
                return self.webRuntime.disconnect(component_src, component_intf, intf_type)
            case 'web_client':
                return self.clientRuntime.disconnect(component_src, component_intf, intf_type)
            case 'web_server':
                return self.serverRuntime.disconnect(component_src, component_intf, intf_type)
            case _:
                raise ConnectionException("Incorrect runtimeType set, must be {plain, web, web_client, or web_server") 

    

    # CREATE - Plain component in the address space
    def create(self, runtimeType:str, moduleType: str, componentName: str) -> component:
        if not componentName.isalnum():
            raise ComponentException("Component name is not alphanumeric")
        match runtimeType:
            case "plain":
                try:
                    return self.plainRuntime.create(moduleType, componentName)
                except PlainComponentException as e:
                    raise ComponentException(e) 

            case 'web':
                return self.webRuntime.create(moduleType, componentName)
            case 'web_client':
                return self.clientRuntime.create(moduleType, componentName)
            case 'web_server':
                return self.serverRuntime.create(componentName, componentName)
            case _:
                raise ComponentException("Incorrect runtimeType set, must be {plain, web, web_client, or web_server") 

    # DELETE - Plain component in the address space
    def delete(self, type, component_id):
        match type:
            case "plain":
                return self.plainRuntime.delete(component_id)
            case 'web':
                return self.webRuntime.delete(component_id)
            case 'web_client':
                return self.clientRuntime.delete(component_id)
            case 'web_server':
                return self.serverRuntime.delete(component_id)
            case _:
                raise ComponentException("Incorrect runtimeType set, must be {plain, web, web_client, or web_server") 
