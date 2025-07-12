import networkx as nx
from MetaInterface.IMetaInterface import IMetaInterface
import matplotlib.pyplot as plt

class MetaArchitecture(IMetaInterface):
    """
    A meta-architecture manager that uses a directed graph to represent components
    and their connections, along with associated metadata for interfaces and receptacles.
    """

    def __init__(self):
        """Initialize the architecture graph and metadata stores."""
        self.G = nx.DiGraph()
        self.components = {}
        self.metaData = {}

    def addNode(self, component_label, component):
        """
        Add a new component node to the architecture graph.

        Args:
            component_label (str): Label for the component.
            component (object): The component instance.

        Returns:
            bool: True if added, False if already exists.
        """
        if component_label in self.G.nodes:
            return False
        self.G.add_node(component_label)
        self.components[component_label] = component
        self.metaData[component_label] = {"Interface": {}, "Receptacle": {}}
        return True

    def removeNode(self, component_label):
        """
        Remove a component node from the architecture graph.

        Args:
            component_label (str): The label of the component to remove.

        Returns:
            bool: True if removed, False if not found.
        """
        if component_label in self.G.nodes:
            self.G.remove_node(component_label)
            self.components.pop(component_label, None)
            self.metaData.pop(component_label, None)
            return True
        return False

    def getLabel(self, component):
        """
        Retrieve the label of a component instance.

        Args:
            component (str or object): Component label or instance.

        Returns:
            str or None: Label if found, else None.
        """
        if isinstance(component, str):
            return component if component in self.G.nodes else None
        return next((k for k, v in self.components.items() if v == component), None)

    def addEdge(self, src, intf, intf_type):
        """
        Add a directed edge between components with interface metadata.

        Args:
            src (str): Source component label.
            intf (str): Target component label.
            intf_type (str): Type of interface.
        """
        self.G.add_edge(src, intf, interface=intf_type)

    def removeEdge(self, src, intf, intf_type):
        """
        Remove an edge between components if interface type matches.

        Args:
            src (str): Source component label.
            intf (str): Target component label.
            intf_type (str): Expected interface type.

        Returns:
            bool: True if removed, False otherwise.
        """
        if self.G.has_edge(src, intf):
            edge_data = self.G.get_edge_data(src, intf)
            if edge_data.get("interface") == intf_type:
                self.G.remove_edge(src, intf)
                return True
            else:
                print(f"Edge exists but interface type does not match: {edge_data}")
        return False

    def visualise(self):
        """Display a visual representation of the architecture graph."""
        pos = nx.spring_layout(self.G)
        nx.draw(self.G, pos, with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(self.G, pos=pos)
        plt.show()

    def connectionsToIntf(self, component_label, intf):
        """
        Get all predecessors connected to a component through a specific interface.

        Args:
            component_label (str): Component label.
            intf (str): Interface name.

        Returns:
            list: List of predecessor component labels.
        """
        return [item for item in self.G.predecessors(component_label)
                if self.G.get_edge_data(item, component_label).get("interface") == intf]

    def connectionsFromRecp(self, component_label, intf):
        """
        Get all successors connected from a component through a specific interface.

        Args:
            component_label (str): Component label.
            intf (str): Interface name.

        Returns:
            list: List of successor component labels.
        """
        return [item for item in self.G.successors(component_label)
                if self.G.get_edge_data(component_label, item).get("interface") == intf]

    def getAllComponents(self):
        """
        Get all component labels in the architecture.

        Returns:
            list: List of component labels.
        """
        return list(self.G.nodes())

    def getComponent(self, label):
        """
        Get the component instance for a given label.

        Args:
            label (str): Component label.

        Returns:
            object: The component instance.
        """
        return self.components.get(label)

    def getInterfaces(self, component_label):
        """
        Get a list of fully qualified interface class names for a component.

        Args:
            component_label (str): Label of the component.

        Returns:
            list: List of class name strings.
        """
        interfaces = self.metaData.get(component_label, {}).get("Interfaces", [])
        class_names = [f"{cls.__module__}.{cls.__name__}" for cls in interfaces]
        return [name for name in class_names if name != "AddasuSec.Component.Component"]

    def getReceptacles(self, component_label):
        """
        Get the receptacle metadata for a component.

        Args:
            component_label (str): Component label.

        Returns:
            dict: Receptacle metadata dictionary.
        """
        return self.metaData.get(component_label, {}).get("Receptacle")

    def setInterfaceAttributeValue(self, component_label, iid, name, value):
        """
        Set an attribute value for a specific interface on a component.

        Args:
            component_label (str): Label of the component.
            iid (str): Interface ID.
            name (str): Attribute name.
            value: Attribute value.
        """
        self.metaData[component_label]["Interface"].setdefault(iid, {})[name] = value

    def getInterfaceAttributeValue(self, component_label, iid, name):
        """
        Get an attribute value from a specific interface on a component.

        Args:
            component_label (str): Label of the component.
            iid (str): Interface ID.
            name (str): Attribute name.

        Returns:
            The value of the specified attribute or None if not found.
        """
        return self.metaData[component_label]["Interface"].get(iid, {}).get(name)

    def setReceptacleAttributeValue(self, component_label, iid, name, value):
        """
        Set an attribute value for a specific receptacle on a component.

        Args:
            component_label (str): Label of the component.
            iid (str): Receptacle ID.
            name (str): Attribute name.
            value: Attribute value.
        """
        self.metaData[component_label]["Receptacle"].setdefault(iid, {})[name] = value

    def getReceptacleAttributeValue(self, component_label, iid, name):
        """
        Get an attribute value from a specific receptacle on a component.

        Args:
            component_label (str): Label of the component.
            iid (str): Receptacle ID.
            name (str): Attribute name.

        Returns:
            The value of the specified attribute or None if not found.
        """
        return self.metaData[component_label]["Receptacle"].get(iid, {}).get(name)

    def setComponentAttributeValue(self, component_label, name, value):
        """
        Set a general metadata attribute for a component.

        Args:
            component_label (str): Label of the component.
            name (str): Attribute name.
            value: Attribute value.
        """
        self.metaData.setdefault(component_label, {})[name] = value

    def getComponentAttributeValue(self, component_label, name):
        """
        Get a general metadata attribute value for a component.

        Args:
            component_label (str): Label of the component.
            name (str): Attribute name.

        Returns:
            The value of the specified attribute or None if not found.
        """
        return self.metaData.get(component_label, {}).get(name)
