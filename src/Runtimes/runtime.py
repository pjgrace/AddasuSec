import importlib
import inspect

from MetaArchitecture.MetaArchitecture import MetaArchitecture
from MetaInterface.IMetaInterface import IMetaInterface


class runtime(IMetaInterface):

    def __init__(self):
        print("intialise runtime")
        self.meta = MetaArchitecture(self)
        self.metaData = {}

    def connect(self, component_src, component_intf, intf_type):
        src_label = self.meta.getLabel(component_src);
        sink_label = self.meta.getLabel(component_intf);
        self.meta.addEdge(src_label, sink_label, intf_type)
        return component_src.connect(component_intf, intf_type)
    
    def removeE(self, all_interfaces, toRemove):
        for index in all_interfaces:
            if index.__name__ == toRemove:
                all_interfaces.remove(index)
                return
                

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
        self.metaData.update({component: {"Interface": {}}})
        interim = self.metaData.get(component)
        interim.update({"Receptacle": {}})
        self.setComponentAttributeValue(component, "Interfaces", all_interfaces)
        self.setComponentAttributeValue(component, "Receptacles", instance.receptacles)
        
        return instance

    def delete(self, component_id):
      self.meta.removeNode(component_id)

    def visualise(self):
        self.meta.visualise()
        
    def getAllComponents(self):
        return self.meta.getAllComponents();
    
    def connectionsToIntf(self, component_label, intf):
        return self.meta.connectionsToIntf(component_label, intf)
    
    def connectionsFromRecp(self, component_label, intf):
        return self.meta.connectionsFromRecp(component_label, intf)
    
    def getInterfaces(self, component_label):
        return self.metaData.get(component_label).get("Interfaces")

    def getReceptacles(self, component_label):
        return self.metaData.get(component_label).get("Receptacles")

    def setInterfaceAttributeValue(self, component_label, iid, name, value):
        interim = self.metaData.get(component_label).get("Interface").get(iid)
        if interim == None:
            interim2 = self.metaData.get(component_label).get("Interface")
            interim2.update({iid: {name:value}}) 
        else:
            interim.update({name: value})
    
    def getInterfaceAttributeValue(self, component_label, iid, name):
        return self.metaData.get(component_label).get("Interface").get(iid).get(name)
    
    def setReceptacleAttributeValue(self, component_label, iid, name, value):
        interim = self.metaData.get(component_label).get("Receptacle").get(iid)
        if interim == None:
            interim2 = self.metaData.get(component_label).get("Receptacle")
            interim2.update({iid: {name:value}}) 
        else:
            interim.update({name: value})
    
    def getReceptacleAttributeValue(self, component_label, iid, name):
        return self.metaData.get(component_label).get("Receptacle").get(iid).get(name)
    
    def setComponentAttributeValue(self, component_label, name, value):
        interim = self.metaData.get(component_label)
        if interim == None:
            self.metaData.update({component_label: {name:value}})
        else:
            interim.update({name: value})
    
    def getComponentAttributeValue(self, component_label, name):
        return self.metaData.get(component_label).get("Component").get(name)
    
    
    
            