import importlib
import inspect

from typing import get_type_hints
from MetaArchitecture.MetaArchitecture import MetaArchitecture
from MetaInterface.IMetaInterface import IMetaInterface
from AddasuSec import WebClientComponent

import threading

class clientRuntime():

    def __init__(self, meta):
        self.meta = meta

    def connect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src.getWrapper());
        sink_label = self.meta.getLabel(component_intf);
        self.meta.addEdge(src_label, sink_label, intf_type)
        
        # Get the outer component body
        comp_src_outer = component_src.getWrapper()
        return comp_src_outer.connect(component_intf, intf_type, self)
    
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


    def create(self, module, component):
        module2 =  importlib.import_module(module)
        class_ = getattr(module2, module.rsplit('.', 1)[-1])
        instance = class_(component)
        distributedComponent = WebClientComponent.WebClientComponent(instance)
        self.meta.addNode(component, distributedComponent)
        instance.setWrapper(distributedComponent)
        
        all_interfaces = list((inspect.getmro(class_)))
        self.removeE(all_interfaces, module.rsplit('.', 1)[-1])
        self.removeE(all_interfaces, "component")
        self.removeE(all_interfaces, "ABC")
        self.removeE(all_interfaces, "object")
        
        self.meta.setComponentAttributeValue(component, "Interfaces", all_interfaces)
        self.meta.setComponentAttributeValue(component, "Receptacles", instance.receptacles)

        return instance

    def delete(self, component_id):
      self.meta.removeNode(component_id)

    # DISCONNECT - Two Component in same address space
    def disconnect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src.getWrapper());
        sink_label = self.meta.getLabel(component_intf);
        self.meta.removeEdge(src_label, sink_label, intf_type)
        try:
            if isinstance(component_src, str):
                component_src = self.meta.getComponent(component_src)
                
            return component_src.getWrapper().disconnect(intf_type)
        except Exception as e:
            raise Exception(f"Receptable-Interface connection failed - {e}")
    

    
            