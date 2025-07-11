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
        def __init__(self, app, port):
            super().__init__()
            self.app = app
            self.port = port
            self.httpd = None
    
        def run(self):
            print(f"Serving on http://127.0.0.1:{self.port}")
            with make_server('', self.port, self.app) as self.httpd:

                # Serve until process is killed
                self.httpd.serve_forever()
            
            
        def stop(self):
            if self.httpd:
                print("Shutting down server...")
                self.httpd.shutdown()
                # Send dummy request to unblock server (force it to wake)
                try:
                    requests.get(f'http://localhost:{self.port}/__shutdown__')
                except Exception:
                    pass  # Ignore any error from the dummy request

class WebComponent:

    innerComponent = None
    receptacles = {}
    
    def __init__(self, component, secure):
        self.innerComponent = component
        for item in component.receptacles:
            rcp = WebReceptacle.WebReceptacle(item)
            self.innerComponent.receptacles[item] = rcp
        
        self.dynamic_routes = {}
        if secure:
            jwt_middleware = JWTAuthMiddleware()
            self.app = falcon.App(middleware=[jwt_middleware])
        else:
            self.app = falcon.App()

        
    def add_route(self, path, resource):
        self.dynamic_routes[path] = resource
        self.app.add_route(path, resource)

    def remove_route(self, path):
        self.dynamic_routes.pop(path, None)
        
    def call_and_serialize(self, method, *args, **kwargs):
        result = method(*args, **kwargs)
        return json.dumps(result)
    
    def startThreadedServer(self, port):
        self.port = port
        self.server = ServerThread(self.app, port)
        self.server.start()
        time.sleep(2)
                
    def stopThreadedServer(self):
        self.server.stop()  # Trigger graceful shutdown
        self.server.join()  # Wait for thread to finish
        print("Done.")

    def on_postt(self, req, resp):
       
        nm= req.path.rpartition('/')[-1]
        methods = [attr for attr in dir(self.innerComponent) if callable(getattr(self.innerComponent, attr)) and not attr.startswith("__")]
        print("Available methods:", methods)

        # Check if the desired method exists
        if nm in methods:
            # Retrieve the method
            method = getattr(self.innerComponent, nm)
            sig = inspect.signature(method)
            
            args = []
            
            for name, param in sig.parameters.items():
                annotation = param.annotation
                # If no annotation, will be inspect._empty
                annotation_str = annotation if annotation != inspect._empty else "No type annotation"
                print(f"  {name}: {annotation_str}")
                args.append(self.get_typed_param(req, name, annotation_str))
            # Dynamically invoke the method with arguments
                
            if inspect.iscoroutinefunction(method):
                result = asyncio.run(method(req, *args))
            else:
                try:
                    result = method(req, *args)
                except Exception as e:
                    result = method(*args)
                    
            print(f"Result of calling {nm}: {result}")
        else:
            print(f"Method '{nm}' not found.")
            description = (
                'Aliens have attacked our base! We will '
                'be back as soon as we fight them off. '
                'We appreciate your patience.'
            )

            raise falcon.HTTPServiceUnavailable(
                title='Service Outage', description=description, retry_after=30
            )


    def on_post(self, req, resp):
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
                annotation_str = annotation if annotation != inspect._empty else "No type annotation"
                print(f"  {name}: {annotation_str}")
                args.append(self.get_typed_param(req, name, annotation_str))
            
            if inspect.iscoroutinefunction(method):
                result = asyncio.run(method(req, *args))
            else:
                try:
                    result = method(req, *args)
                except Exception as e:
                    result = method(*args)
            
            print(f"Result of calling {nm}: {result}")
            return_annotation = sig.return_annotation
    
            # ✅ Clean response
            resp.media = {"result": result}
            resp.set_header('Powered-By', 'Falcon')
            resp.status = falcon.HTTP_200
    
        else:
            print(f"Method '{nm}' not found.")
            description = (
                'The method called is not implemented on the component.'
            )
    
            raise falcon.HTTPServiceUnavailable(
                title='Service Outage', description=description, retry_after=30
            )

        
    def get_typed_param(self, req: falcon.Request, name: str, param_type: type):
        """
        Retrieve a typed parameter from a Falcon request.
        
        Supported types:
            - str
            - int
            - float
            - bool
            - datetime.date (ISO format: YYYY-MM-DD)
            - uuid.UUID
            - dict (JSON string parsed into dict)
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
            except (ValueError, json.JSONDecodeError) as e:
                raise TypeError(f"Unsupported type: {param_type.__name__}")
    
        return value

    def connect(self, component, intf, rt):
        try:
            return self.innerComponent.receptacles.get(intf).connect(component, intf, rt)
        except ValueError:
            return False
        
    def disconnect(self, component, intf, rt):
        try:
            return self.innerComponent.receptacles.get(intf).disconnect(intf)
        except ValueError:
            return False
    
    
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