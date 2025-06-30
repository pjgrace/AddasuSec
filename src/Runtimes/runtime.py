import importlib
import inspect
from Runtimes.ComponentRuntime import ComponentRuntime
from Runtimes.rpcRuntime import rpcRuntime
from Runtimes.clientRuntime import clientRuntime
from Runtimes.serverRuntime import serverRuntime

from MetaArchitecture.MetaArchitecture import MetaArchitecture
from networkx.generators.tests.test_small import null


class runtime():
    
    def __init__(self, meta):
        print("intialise runtime")
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
                return self.plainRuntime.connect(component_src, component_intf, intf_type)
            case 'web':
                return self.webRuntime.connect(component_src, component_intf, intf_type)
            case 'web_client':
                return self.clientRuntime.connect(component_src, component_intf, intf_type)
            case 'web_server':
                return self.serverRuntime.connect(component_src, component_intf, intf_type)
            case _:
                return 0   # 0 is the default case if x is not found
    
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
                return 0   # 0 is the default case if x is not found
    

    # CREATE - Plain component in the address space
    def create(self, type, module, component):
        match type:
            case "plain":
                return self.plainRuntime.create(module, component)
            case 'web':
                return self.webRuntime.create(module, component)
            case 'web_client':
                return self.clientRuntime.create(module, component)
            case 'web_server':
                return self.serverRuntime.create(module, component)
            case _:
                return 0   # 0 is the default case if x is not found

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
                return 0   # 0 is the default case if x is not found
