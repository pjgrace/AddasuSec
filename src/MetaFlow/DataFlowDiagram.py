import networkx as nx
import matplotlib.pyplot as plt
import inspect

class DataFlowDiagram:
    """
    A class to represent a Data Flow Diagram (DFD) using a directed graph.
    Nodes can represent Processes, Data Stores, or External Entities.
    Edges represent data flows between these nodes.
    """

    def __init__(self, meta):
        """Initialize the data flow graph and node metadata."""
        self.graph = nx.DiGraph()
        self.node_types = {}      # Maps node -> type (e.g., Process, DataStore, ExternalEntity)
        self.edge_data = {}       # Maps (src, dst) -> data type or schema
        self.meta = meta
        
    def add_node(self, label, node_type):
        """
        Add a node to the DFD.

        Args:
            label (str): The name of the node.
            node_type (str): The type (Process, DataStore, ExternalEntity).
        """
        self.graph.add_node(label)
        self.node_types[label] = node_type

    def add_data_flow(self, source, destination, data_type):
        """
        Add a directed edge (data flow) between two nodes.

        Args:
            source (str): Source node label.
            destination (str): Destination node label.
            data_type (str): Description of the data.
        """
        self.graph.add_edge(source, destination, data=data_type)
        self.edge_data[(source, destination)] = data_type

    def get_node_type(self, label):
        """Get the type of a node."""
        return self.node_types.get(label)

    def get_data_flow(self, source, destination):
        """Get the data type or schema flowing between two nodes."""
        return self.edge_data.get((source, destination))

    def visualize(self):
        """Visualize the DFD with node types and edge labels."""
        pos = nx.spring_layout(self.graph)
        node_colors = []
        for node in self.graph.nodes():
            if self.node_types[node] == "Process":
                node_colors.append("skyblue")
            elif self.node_types[node] == "DataStore":
                node_colors.append("lightgreen")
            elif self.node_types[node] == "ExternalEntity":
                node_colors.append("salmon")
            else:
                node_colors.append("grey")

        nx.draw(self.graph, pos, with_labels=True, node_color=node_colors, node_size=2000, font_size=10)
        edge_labels = nx.get_edge_attributes(self.graph, 'data')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_color='black')
        plt.title("Data Flow Diagram")
        plt.show()

    def get_all_nodes(self):
        """Return a list of all nodes."""
        return list(self.graph.nodes())

    def get_all_data_flows(self):
        """Return a list of all data flows (edges)."""
        return list(self.graph.edges(data=True))

    def is_data_store(self, component, label):
            # Check meta attribute first
            if self.meta.getComponentAttributeValue(label, "data_store_component") is True:
                return True
            # If not found in meta, check for decorator on any method
            for _, method in inspect.getmembers(component.__class__, predicate=inspect.isfunction):
                if getattr(method, '__data_store__', False):
                    return True
            return False
        
    def is_external_store(component, label):
            # Check meta attribute first
            if meta.getComponentAttributeValue(label, "external_entity_component") is True:
                return True
            # If not found in meta, check for decorator on any method
            for _, method in inspect.getmembers(component.__class__, predicate=inspect.isfunction):
                if getattr(method, '__data_store__', False):
                    return True
            return False

    def from_meta_architecture(self, meta: MetaArchitecture):
        """Convert a MetaArchitecture graph to a DFD graph.

        Args:
            meta (MetaArchitecture): The meta architecture instance.
        """
        import inspect

        # Add nodes based on annotation conventions
        for label in meta.getAllComponents():
            component = meta.getComponent(label)
            class_name = component.__class__.__name__.lower()

            if 'data' in class_name or 'label' in class_name:
                node_type = 'datastore'
            elif 'input' in class_name or 'output' in class_name:
                node_type = 'external_entity'
            else:
                node_type = 'process'

            self.add_node(label, node_type)

        # Add edges with data sets derived from interface parameter names
        for src, dst, attrs in meta.G.edges(data=True):
            interface_cls = attrs.get("interface")
            data_names = set()

            if inspect.isclass(interface_cls):
                for _, method in inspect.getmembers(interface_cls, predicate=inspect.isfunction):
                    sig = inspect.signature(method)
                    data_names.update(param.name for param in sig.parameters.values() if param.name != 'self')

            self.add_data_flow(src, dst, data_names)
