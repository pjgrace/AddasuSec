import falcon
import inspect
import datetime
import uuid
import json
from AddasuSec import WebReceptacle
from networkx.generators.tests.test_small import null

class WebComponent:

    innerComponent = null
    receptacles = {}
    secure=False
    
    def __init__(self, component):
        self.innerComponent = component
        for item in component.receptacles:
            rcp = WebReceptacle.WebReceptacle(item)
            self.innerComponent.receptacles[item] = rcp
            
    def call_and_serialize(self, method, *args, **kwargs):
        result = method(*args, **kwargs)
        return json.dumps(result)
    
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        resp.media = {
            'quote': "I've always been more interested in the future than in the past.",
            'author': 'Grace Hopper',
        }
        
    def on_post(self, req, resp):
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
            result = method(*args)
            print(f"Result of calling {nm}: {result}")
            return_annotation = sig.return_annotation
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

        # NOTE: Normally you would use resp.media for this sort of thing;
        # this example serves only to demonstrate how the context can be
        # used to pass arbitrary values between middleware components,
        # hooks, and resources.
        
        resp.media = {f'{sig.return_annotation}': result}

        resp.set_header('Powered-By', 'Falcon')
        resp.status = falcon.HTTP_200
        print(resp)
        
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
        
    def setSecure(self, value):
        self.secure = value