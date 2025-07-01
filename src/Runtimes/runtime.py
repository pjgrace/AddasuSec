from Runtimes.ComponentRuntime import ComponentRuntime, PlainComponentException,\
    PlainConnectionException
from Runtimes.rpcRuntime import rpcRuntime
from Runtimes.clientRuntime import clientRuntime
from Runtimes.serverRuntime import serverRuntime
from AddasuSec.component import component
import requests
import importlib
import inspect
import json
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

    # CREATE - Plain component in the address space
    def remoteCreate(self, url, runtimeType:str, moduleType: str, componentName: str) -> component:
        if not componentName.isalnum():
            raise ComponentException("Component name is not alphanumeric")
        try:
            return self.createRemoteComponent(url, runtimeType, moduleType, componentName)
        except Exception as e:
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

    def createRemoteComponent(self, url, type_, module, component):
        module2 =  importlib.import_module(module)
        class_ = getattr(module2, module.rsplit('.', 1)[-1])
        all_interfaces = list((inspect.getmro(class_)))
        self.removeE(all_interfaces, module.rsplit('.', 1)[-1])
        self.removeE(all_interfaces, "component")
        self.removeE(all_interfaces, "ABC")
        self.removeE(all_interfaces, "object")
        instance = class_(component)
        self.meta.addNode(component, instance)
        

        self.meta.setComponentAttributeValue(component, "Interfaces", all_interfaces)
        self.meta.setComponentAttributeValue(component, "Receptacles", instance.receptacles)

        resp = requests.post(f"{url}/create", json={
            "type": type_,
            "module": module,
            "component": component
        })
        reply = json.loads(resp.text)
        url = reply["result"]
        self.meta.setComponentAttributeValue(component, "Host",  f"{url}")
        return component

    def delete_component(self, url, type_, component_id):
        resp = requests.post(f"{url}/delete", json={
            "type": type_,
            "component_id": component_id
        })
        print(resp.json())

    def connect_components(self, url, type_, src, intf, intf_type):
        resp = requests.post(f"{url}/connect", json={
            "type": type_,
            "component_src": src,
            "component_intf": intf,
            "intf_type": intf_type
        })
        print(resp.json())

    def disconnect_components(self, url, type_, src, intf, intf_type):
        resp = requests.post(f"{url}/disconnect", json={
            "type": type_,
            "component_src": src,
            "component_intf": intf,
            "intf_type": intf_type
        })
        print(resp.json())
        
    def removeE(self, all_interfaces, toRemove):
        for index in all_interfaces:
            if index.__name__ == toRemove:
                all_interfaces.remove(index)
                return
