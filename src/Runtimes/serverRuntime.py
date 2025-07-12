import importlib
import inspect
from typing import get_type_hints
from MetaArchitecture.MetaArchitecture import MetaArchitecture
from MetaInterface.IMetaInterface import IMetaInterface
from AddasuSec import WebServerComponent
from wsgiref.simple_server import make_server
import falcon
from Runtimes.Auth.JWTMiddleware import JWTAuthMiddleware

import random
import threading

class serverRuntime():

    def __init__(self, meta):
        self.meta = meta
        self.port = 8000
        #user_loader = lambda username, password: { 'username': username }
        #auth_backend = BasicAuthBackend(user_loader)
        #auth_middleware = FalconAuthMiddleware(auth_backend,
        #                    exempt_routes=['/exempt'], exempt_methods=['HEAD'])
        #self.app = falcon.App(middleware=[auth_middleware])
        
        
    def threaded_function(self, app, port):
        with make_server('', port, app) as httpd:
            print(f"Serving on port {port}...")

            # Serve until process is killed
            httpd.serve_forever()
        
    def authenticate(self, user, password):
        # Check if the user exists and the password match.
        # This is just for the example
        return random.choice((True, False))


    def basic_user_loader(self, attributes, user, password):
        if self.authenticate(user, password):
            return {"username": user, "kind": "basic"}
        return None

    def connect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src);
        sink_label = self.meta.getLabel(component_intf);
        self.meta.addEdge(src_label, sink_label, intf_type)
        if isinstance(component_src, str):
            component_src = self.meta.getComponent(component_src)
        return component_src.connect(component_intf, intf_type)
    
    # DISCONNECT - Two Component in same address space
    def disconnect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src);
        sink_label = self.meta.getLabel(component_intf);
        self.meta.removeEdge(src_label, sink_label, intf_type)
        if isinstance(component_src, str):
            component_src = self.meta.getComponent(component_src)
        return component_src.disconnect(intf_type)
    
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

    def get_instance_methods(self, instance):
        return [
            (name, getattr(instance, name))
            for name in dir(instance)
            if callable(getattr(instance, name)) and not name.startswith("__")
        ]

    def create(self, module, component, secure):
        module2 =  importlib.import_module(module)
        class_ = getattr(module2, module.rsplit('.', 1)[-1])
        instance = class_(component)
        instance.setSecure(secure)
        distributedComponent = WebServerComponent.WebServerComponent(instance)
        self.meta.addNode(component, distributedComponent)
        
        all_interfaces = list((inspect.getmro(class_)))
        self.removeE(all_interfaces, module.rsplit('.', 1)[-1])
        self.removeE(all_interfaces, "component")
        self.removeE(all_interfaces, "ABC")
        self.removeE(all_interfaces, "object")
        
        if secure:
            jwt_middleware = JWTAuthMiddleware()
            app = falcon.App(middleware=[jwt_middleware])
        else:
            app = falcon.App()
        print(f"API is {app}")
        thread = threading.Thread(target = self.threaded_function, args = (app, self.port,  ))
        thread.start()
        
        for intf in all_interfaces:
            methods = [attr for attr in dir(intf) if callable(getattr(intf, attr)) and not attr.startswith("__")]
            for meth in methods:
                path = self.meta.getLabel(distributedComponent)
                route = f'/{path}/{meth}'
                print(route)
                app.add_route(route, distributedComponent)
        
        self.meta.setComponentAttributeValue(component, "Host",  f"localhost:{self.port}")

        self.meta.setComponentAttributeValue(component, "Interfaces", all_interfaces)
        self.meta.setComponentAttributeValue(component, "Receptacles", instance.receptacles)

        self.port+=1
        return distributedComponent

    def delete(self, component_id):
      self.meta.removeNode(component_id)
