from collections.abc import ValuesView

import xmlrpc.client
import requests
import json
from requests.auth import HTTPBasicAuth
import inspect
import importlib
from pydoc import locate


class rpcReceptacle:
    def __init__(self, id):
        self.iid = id
        self._Comp = None
        self.m_connID = -1
        self.meta_Data = {}
        self.url = 'http://'
        
    def __getattr__(self, nameA):
        def method(*args, **kwargs):
            print(f"Called method: {nameA}")
            print(f"  Positional args: {args}")
            print(f"  Keyword args: {kwargs}")
            print(f"{nameA} executed")
            self.url += nameA
            sig = self.get_method_signature_from_class_name(self.iid, nameA)
            return_annotation = sig.return_annotation
            print("Return type from signature:", return_annotation)
            
            if sig.parameters:
                self.url += '?'
            i=0;
            for name, param in sig.parameters.items():
                if not name=="self":
                    annotation = param.annotation
                    # If no annotation, will be inspect._empty
                    annotation_str = annotation if annotation != inspect._empty else "No type annotation"
                    print(f"  {name}: {annotation_str}")
                    self.url += f"{name}={args[i]}&"
                    i+=1
                    
            if i>0:
                self.url = self.url[:-1]
                
            basic = HTTPBasicAuth('user', 'pass')

            x = requests.post(self.url, auth=basic)

            y = json.loads(x.text)
            
            extracted_value = None
            for key, value in y.items():
                if isinstance(value, return_annotation):
                    extracted_value = value
                    print(f"Matched key: {key}, Value: {value}")
                    break
            
            if extracted_value is None:
                print("No matching value found.")

            # the result is a Python dictionary:
            #return y["sum"]            
            return extracted_value
        return method
    
    def dynamic_call(self, name: str, *args, **kwargs):
        do = f"get_{name}"
        if hasattr(self, do) and callable(getattr(self, do)):
            func = getattr(self, do)
            return func(*args, **kwargs)

    def get_method_signature_from_class_name(self, class_name: str, method_name: str):
        # Locate the class using full path, e.g., 'Examples.IAdd'
         # Import the module (e.g., 'Examples')
        module = importlib.import_module(class_name)
        classname = class_name.split('.')[-1]
                # Get the class
        cls = getattr(module, classname, None)

        if cls is None:
            raise NameError(f"Class '{class_name}' not found in module '{class_name}'")
        if not isinstance(cls, type):
            raise TypeError(f"'{class_name}' is not a class. Got: {type(cls)}")

        # Look for method in class __dict__ to bypass descriptor wrappers like @abstractmethod
        raw_method = cls.__dict__.get(method_name, None)
        if raw_method is None:
            raise AttributeError(f"Method '{method_name}' not found directly in class '{class_name}'")

        # Unwrap staticmethod/classmethod if needed
        if isinstance(raw_method, (staticmethod, classmethod)):
            func = raw_method.__func__
        else:
            func = raw_method

        # Now get signature
        sig = inspect.signature(func)
        return sig

    def connect(self, pIUnkSink, riid, rt):
        if(riid!=self.iid):
            return False
        self._Comp = self
        compName = rt.meta.getLabel(pIUnkSink)
        self.url += rt.getComponentAttributeValue(compName, "Host") + f"/{compName}/"
        
        #xmlrpc.client.ServerProxy("http://localhost:8000")
        return True

    def disconnect(self, id):
        if(id!=self.m_connID):
            return False
        self._Comp = None
        return True

    def putData(self, name, value):
        self.meta_Data.update([name, value])

    def getValue(self, name):
      return self.meta_Data.get(name)

    def getValues(self):
      return self.meta_Data.keys
        