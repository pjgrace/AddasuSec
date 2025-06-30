import importlib
import inspect

from MetaArchitecture.MetaArchitecture import MetaArchitecture

class ComponentRuntime():

    def __init__(self, meta):
        print("intialise runtime")
        self.meta = meta
        
    # CONNECT - Two Component in same address space.
    
    # This is the connect of two local address space components
    # The causal connection updates the global meta model with the
    # meta data
    def connect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src);
        sink_label = self.meta.getLabel(component_intf);
        self.meta.addEdge(src_label, sink_label, intf_type)
        return component_src.connect(component_intf, intf_type)
    
    # DISCONNECT - Two Component in same address space
    def disconnect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src);
        sink_label = self.meta.getLabel(component_intf);
        self.meta.removeEdge(src_label, sink_label, intf_type)
        return component_src.disconnect(component_intf, intf_type)
    

    # CREATE - Plain component in the address space
    def create(self, module, component):
        module2 =  importlib.import_module(module)
        class_ = getattr(module2, module.rsplit('.', 1)[-1])
        instance = class_(component)
        
        all_interfaces = list((inspect.getmro(class_)))
        self.removeE(all_interfaces, module.rsplit('.', 1)[-1])
        self.removeE(all_interfaces, "component")
        self.removeE(all_interfaces, "ABC")
        self.removeE(all_interfaces, "object")

        self.meta.addNode(component, instance)
        
        self.meta.setComponentAttributeValue(component, "Interfaces", all_interfaces)
        self.meta.setComponentAttributeValue(component, "Receptacles", instance.receptacles)
        
        return instance
     
    #Local method used by create to remove Python interfaces from the object
    def removeE(self, all_interfaces, toRemove):
        for index in all_interfaces:
            if index.__name__ == toRemove:
                all_interfaces.remove(index)
                return

    # DELETE - Plain component in the address space
    def delete(self, component_id):
        self.meta.removeNode(component_id)
