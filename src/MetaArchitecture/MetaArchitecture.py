#import matplotlib.pyplot as plt
import networkx as nx
from MetaInterface.IMetaInterface import IMetaInterface
import matplotlib.pyplot as plt

class MetaArchitecture(IMetaInterface):
    def __init__(self):
        self.G = nx.DiGraph()
        self.components = {}
        self.metaData = {}

    def addNode(self, component_label, component):
        if list(self.G.nodes).__contains__(component_label):
            return False
        else:
            self.G.add_node(component_label)
            self.components.update({component_label: component})
            self.metaData.update({component_label: {"Interface": {}}})
            interim = self.metaData.get(component_label)
            interim.update({"Receptacle": {}})
            return True

    def removeNode(self, component_label):
        if list(self.G.nodes).__contains__(component_label):
            self.G.remove_node(component_label)
            self.components.pop(component_label)
            return True
        else:
            return False
  
    def getLabel(self, component):
        for key, value in self.components.items():
            if component == value:
                return key
  
    def addEdge(self, src, intf, intf_type):
        self.G.add_edge(src, intf, interface = intf_type)

    def removeEdge(self, src, intf):
        self.G.remove_edge(src, intf)

    def visualise(self):
        nx.draw(self.G, with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(self.G, pos=nx.spring_layout(self.G))
        plt.show()
    
    def connectionsToIntf(self, component_label, intf):
        ret_list = []
        a = list(self.G.predecessors((component_label)))
        for item in a:
            attr = self.G.get_edge_data(item, component_label, None)
            if(attr.get("interface")==intf):
                ret_list.append(item)
            
        return ret_list
    
    def connectionsFromRecp(self, component_label, intf):
        ret_list = []
        a = list(self.G.successors((component_label)))
        for item in a:
            attr = self.G.get_edge_data(component_label, item, None)
            if(attr.get("interface") == intf):
                ret_list.append(item)
            
        return ret_list
    
    def getAllComponents(self):
        return list(self.G.nodes())

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
            self.metaData.get(component_label).update({name: value})
    
    def getComponentAttributeValue(self, component_label, name):
        return self.metaData.get(component_label).get(name)
    
    