"""
WebReceptacle Module

This module defines the WebReceptacle class, which simulates a networked component connector.
It supports dynamic method calling over HTTP using method introspection and signature reflection.
Designed to simulate a remote procedure call pattern by encoding method parameters into a URL.

Classes:
    WebReceptacle: Represents a remote or proxy receptacle for interacting with web services.

Dependencies:
    - requests
    - json
    - requests.auth.HTTPBasicAuth
    - inspect
    - importlib
"""

import requests
import json
from requests.auth import HTTPBasicAuth
import inspect
import importlib

class WebReceptacle:
    def __init__(self, iden):
        self.iid = iden
        self._Comp = None
        self.m_connID = -1
        self.meta_Data = {}
        self.url = 'http://'

    def __getattr__(self, nameA):
        def method(*args, **kwargs):
            print(f"Called method: {nameA}")
            print(f"  Positional args: {args}")
            print(f"  Keyword args: {kwargs}")
            self.url += nameA

            sig = self.get_method_signature_from_class_name(self.iid, nameA)
            return_annotation = sig.return_annotation
            print("Return type from signature:", return_annotation)

            if sig.parameters:
                self.url += '?'

            i = 0
            for name, param in sig.parameters.items():
                if name != "self":
                    annotation = param.annotation
                    annotation_str = annotation if annotation != inspect._empty else "No type annotation"
                    print(f"  {name}: {annotation_str}")
                    self.url += f"{name}={args[i]}&"
                    i += 1

            if i > 0:
                self.url = self.url[:-1]

            basic = HTTPBasicAuth('user', 'pass')
            response = requests.post(self.url, auth=basic)
            y = json.loads(response.text)

            extracted_value = None
            for key, value in y.items():
                if isinstance(value, return_annotation):
                    extracted_value = value
                    print(f"Matched key: {key}, Value: {value}")
                    break

            if extracted_value is None:
                print("No matching value found.")

            return extracted_value

        return method

    def dynamic_call(self, name: str, *args, **kwargs):
        """Dynamically calls a method named 'get_<name>' if available."""
        do = f"get_{name}"
        if hasattr(self, do) and callable(getattr(self, do)):
            func = getattr(self, do)
            return func(*args, **kwargs)

    def get_method_signature_from_class_name(self, class_name: str, method_name: str):
        """Retrieve the signature of a method from a class using reflection."""
        module = importlib.import_module(class_name)
        classname = class_name.split('.')[-1]
        cls = getattr(module, classname, None)

        if cls is None:
            raise NameError(f"Class '{class_name}' not found in module '{class_name}'")
        if not isinstance(cls, type):
            raise TypeError(f"'{class_name}' is not a class. Got: {type(cls)}")

        raw_method = cls.__dict__.get(method_name, None)
        if raw_method is None:
            raise AttributeError(f"Method '{method_name}' not found directly in class '{class_name}'")

        func = raw_method.__func__ if isinstance(raw_method, (staticmethod, classmethod)) else raw_method
        return inspect.signature(func)

    def connect(self, pIUnkSink, riid, rt):
        """Connects to another component via the provided receptacle interface."""
        if riid != self.iid:
            return False

        self._Comp = self
        compName = rt.meta.getLabel(pIUnkSink)
        self.url += rt.meta.getComponentAttributeValue(compName, "Host") + f"/{compName}/"
        return True

    def disconnect(self, iden):
        """Disconnects a component based on its identity."""
        if iden != self.iid:
            return False
        self._Comp = None
        return True

    def putData(self, name, value):
        """Store metadata key-value pair."""
        self.meta_Data.update([name, value])

    def getValue(self, name):
        """Retrieve a value from the stored metadata."""
        return self.meta_Data.get(name)

    def getValues(self):
        """Returns all metadata keys."""
        return self.meta_Data.keys

    def receptacle_with_token(self, func, *args, **kwargs):
        """Performs a token-authenticated method call using context from a previous frame."""
        stack = inspect.stack()
        previous_frame = stack[2].frame
        prev_args = previous_frame.f_locals
        print("Previous call's arguments:", prev_args)

        req = prev_args['req']
        token = None
        if hasattr(req, "get_header") and callable(req.get_header):
            auth_header = req.get_header("Authorization", default=None)
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header[7:]
        else:
            token = req

        nameA = inspect.stack()[1].function
        self.url += nameA

        sig = self.get_method_signature_from_class_name(self.iid, nameA)
        return_annotation = sig.return_annotation
        print("Return type from signature:", return_annotation)

        if sig.parameters:
            self.url += '?'
        i = 0
        for name, param in sig.parameters.items():
            if name != "self":
                annotation = param.annotation
                annotation_str = annotation if annotation != inspect._empty else "No type annotation"
                print(f"  {name}: {annotation_str}")
                self.url += f"{name}={args[i]}&"
                i += 1

        if i > 0:
            self.url = self.url[:-1]

        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.post(self.url, headers=headers)
        y = json.loads(response.text)

        extracted_value = None
        for key, value in y.items():
            if isinstance(value, return_annotation):
                extracted_value = value
                print(f"Matched key: {key}, Value: {value}")
                break

        if extracted_value is None:
            print("No matching value found.")

        return extracted_value
