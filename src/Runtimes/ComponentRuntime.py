import importlib
import inspect

from MetaArchitecture.MetaArchitecture import MetaArchitecture

# Exception raised during creation and deletion of components.
class PlainComponentException(Exception):
    pass

# Exception raised during connection and disconnection of components.
class PlainConnectionException(Exception):
    pass

class ComponentRuntime():

    def __init__(self, meta):
        self.meta = meta
        
    # CONNECT - Two Component in same address space.
    
    # This is the connect of two local address space components
    # The causal connection updates the global meta model with the
    # meta data
    def connect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src);
        if src_label is None:
            raise PlainConnectionException("Source component does not exist")
        sink_label = self.meta.getLabel(component_intf);
        if sink_label is None:
            raise PlainConnectionException("Sink component does not exist")
        self.meta.addEdge(src_label, sink_label, intf_type)
        try:
            if isinstance(component_src, str):
                component_src = self.meta.getComponent(component_src)
                
            return component_src.connect(component_intf, intf_type)
        except Exception as e:
            raise PlainConnectionException(f"Receptable-Interface connection failed - {e}")
    
    # DISCONNECT - Two Component in same address space
    def disconnect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src);
        sink_label = self.meta.getLabel(component_intf);
        self.meta.removeEdge(src_label, sink_label, intf_type)
        return component_src.disconnect(intf_type)
    
    # CREATE - Plain component in the address space
    def create(self, module, component, secure):
        try:
            module2 =  importlib.import_module(module)
            class_ = getattr(module2, module.rsplit('.', 1)[-1])
            instance = class_(component)
            
            all_interfaces = list((inspect.getmro(class_)))
            self.removeE(all_interfaces, module.rsplit('.', 1)[-1])
            self.removeE(all_interfaces, "component")
            self.removeE(all_interfaces, "ABC")
            self.removeE(all_interfaces, "object")
        except Exception as e:
            raise PlainComponentException(f"Component creation {component} failed - {e}")
        if not self.meta.addNode(component, instance):
            raise PlainComponentException("Component id already in use")
        
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
        return self.meta.removeNode(component_id)
