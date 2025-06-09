from abc import ABC, abstractmethod

class IMetaInterface(ABC):
    @abstractmethod
    def getInterfaces(self, component_label):
        pass

    @abstractmethod
    def getReceptacles(self):
        pass
    
    @abstractmethod
    def setInterfaceAttributeValue(self, comp_label, iid, name, value):
        pass

    @abstractmethod
    def getInterfaceAttributeValue(self, comp_label, iid, name):
        pass

    @abstractmethod
    def setReceptacleAttributeValue(self, iid, name, value):
        pass

    @abstractmethod
    def getReceptacleAttributeValue(self, iid, name):
        pass

    @abstractmethod
    def setComponentAttributeValue(self, name, value):
        pass

    @abstractmethod
    def getComponentAttributeValue(self, name):
        pass
