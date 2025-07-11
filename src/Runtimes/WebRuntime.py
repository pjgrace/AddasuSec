import importlib
import inspect
from typing import get_type_hints
from AddasuSec import WebComponent
import random

# Exception raised during connection and disconnection of components.
class WebConnectionException(Exception):
    pass

# Exception raised during creation and deletion of components.
class WebComponentException(Exception):
    pass

class WebRuntime():

    def __init__(self, meta):
        self.meta = meta
        self.port = 8000
        
    def authenticate(self, user, password):
        # Check if the user exists and the password match.
        # This is just for the example
        return random.choice((True, False))

    def basic_user_loader(self, attributes, user, password):
        if self.authenticate(user, password):
            return {"username": user, "kind": "basic"}
        return None
    
    def is_wrapped_by_role_required(self, method):
        """
        Detect if the method has been wrapped by the `role_required` decorator.
        Works on bound or unbound methods.
        """
        # If bound method, get the actual function
        #func = getattr(method, "__func__", method)
        #print(func)
        # Unwrap all the way
        #while True:
        if getattr(method, "_is_role_required", False):
            return True
        elif not hasattr(method, "__wrapped__"):
            func = method.__wrapped__  # Might still be a bound method
            func = getattr(func, "__func__", func)  # Unwrap if wrapped bound method
            if getattr(func, "_is_role_required", False):
                return True
        else:
            return False

    def connect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src);
        sink_label = self.meta.getLabel(component_intf);
        self.meta.addEdge(src_label, sink_label, intf_type)
        try:
            if isinstance(component_src, str):
                component_src = self.meta.getComponent(component_src)
                
            return component_src.connect(component_intf, intf_type, self)
        except Exception as e:
            raise WebConnectionException(f"Receptable-Interface connection failed - {e}")
    
    def disconnect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src);
        sink_label = self.meta.getLabel(component_intf);
        self.meta.removeEdge(src_label, sink_label, intf_type)
        try:
            if isinstance(component_src, str):
                component_src = self.meta.getComponent(component_src)
                
            return component_src.disconnect(component_intf, intf_type, self)
        except Exception as e:
            raise WebConnectionException(f"Receptable-Interface connection failed - {e}")
    
    
    def removeE(self, all_interfaces, toRemove):
        for index in all_interfaces:
            if index.__name__ == toRemove:
                all_interfaces.remove(index)
                return

    def reflect_class(self, cls):
        methods = inspect.getmembers(cls, predicate=inspect.isfunction)
        for name, method in methods:
            if name.startswith("__") and name.endswith("__"):
                continue  # Skip dunder methods

            signature = inspect.signature(method)
            type_hints = get_type_hints(method)

            print(f"Method: {name}")
        
            # Parameters
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                annotation = type_hints.get(param_name, 'Any')
                print(f"  Param: {param_name} ({annotation})")

        # Return type
        return_type = type_hints.get('return', 'Any')
        print(f"  Returns: {return_type}\n")


    def create(self, module, component, secure):
        try:
            module2 =  importlib.import_module(module)
            class_ = getattr(module2, module.rsplit('.', 1)[-1])
            instance = class_(component)
            distributedComponent = WebComponent.WebComponent(instance, secure)
            if not self.meta.addNode(component, distributedComponent):
                raise WebComponentException("Component id already in use")
            
            all_interfaces = list((inspect.getmro(class_)))
            self.removeE(all_interfaces, module.rsplit('.', 1)[-1])
            self.removeE(all_interfaces, "component")
            self.removeE(all_interfaces, "ABC")
            self.removeE(all_interfaces, "object")
            
            for intf in all_interfaces:
                excluded_methods = {
                    "call_with_token", "connect", "disconnect",
                    "getReceptacle", "getWrapper", "component", "ABC", "object",
                    "receptacle_with_token", "setSecure", "setWrapper"
                }
                # Get all callable methods except excluded and dunder
                methods = [
                    name for name, value in inspect.getmembers(intf, predicate=callable)
                    if not name.startswith('_') and name not in excluded_methods
                ]
                for meth in methods:
                    path = self.meta.getLabel(distributedComponent)
                    #self.dynamic_routes[f'/{path}/{meth}'] = distributedComponent
                    path = f'/{path}/{meth}'
                    print(path)
                    distributedComponent.add_route(path, distributedComponent)
                    #self.route_table[path] = distributedComponent
                    #app.add_route(route, distributedComponent)
        except Exception as e:
            raise WebComponentException(f"Component creation {component} failed - {e}")
        
        
        self.meta.setComponentAttributeValue(component, "Host",  f"localhost:{self.port}")
        self.meta.setComponentAttributeValue(component, "Interfaces", all_interfaces)
        self.meta.setComponentAttributeValue(component, "Receptacles", instance.receptacles)
        
        distributedComponent.startThreadedServer(self.port)
        self.port+=1
        
        return distributedComponent

    def delete(self, component_id):
        try:
            comp = self.meta.getComponent(component_id)
            if comp == None:
                return False
            self.meta.removeNode(component_id)
            comp.stopThreadedServer()
            return True;
        except Exception as e:
            return False

    def start(self, component_id):
        comp = self.meta.getComponent(component_id)
        return comp.innerComponent.start()

    
            