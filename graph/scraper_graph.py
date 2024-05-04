# Standard
import json
import logging

# Node and edge dataclasses
from graph.node import Node
from graph.edge import Edge


class ScraperGraph:
    """TODO write class description"""
    def __init__(self):
        """TODO write method description"""
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []

    def add_node(self, node):
        """Add a node to the graph."""
        self.nodes.append(node)

    def add_edge(self, edge):
        """Add an edge to the graph."""
        self.edges.append(edge)

    def serialize(self):
        """Transform the graph to a dictionary representation."""
        return {
            "nodes": [node.serialize() for node in self.nodes],
            "edges": [edge.serialize() for edge in self.edges]
        }

    def save_to_file(self, file_path: str):
        """Save the graph to a file."""
        with open(file_path, "w") as file:
            json.dump(self.serialize(), file)

    @classmethod
    def deserialize(cls, graph_dict: dict[str, any]) -> "ScraperGraph":
        """Compose a graph from a dictionary representation."""
        graph = cls()
        for node_dict in graph_dict["nodes"]:
            node = Node.deserialize(node_dict)
            graph.add_node(node)
        for edge_dict in graph_dict["edges"]:
            edge = Edge.deserialize(edge_dict)
            graph.add_edge(edge)
        return graph

    @classmethod
    def from_file(cls, file_path: str) -> "ScraperGraph":
        """Create a graph from a file."""
        with open(file_path, "r") as file:
            graph_dict = json.load(file)
        return cls.deserialize(graph_dict)


if __name__ == "__main__":
    from node_functions.flow_control_functions import pass_through
    logging.basicConfig(level=logging.INFO)

    # Create a graph
    graph = ScraperGraph()
    node1 = Node(id=1, function=pass_through, input={"input": 1})
    node2 = Node(id=2, function=pass_through, input={"input": 2})
    graph.add_node(node1)
    graph.add_node(node2)
    edge = Edge(source_id=1, target_id=2, use_output_as_input=True)

    # Save the graph to a file
    graph.save_to_file("graph.json")
    graph_from_file = ScraperGraph.from_file("graph.json")

    # Check if the graph is the same
    assert graph.serialize() == graph_from_file.serialize()
    print(graph.serialize())
    print(graph_from_file.serialize())
    print("Graph saved and loaded successfully.")

