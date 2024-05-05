# Standard
import json
import logging
from collections import defaultdict

# Node dataclasses
from graph.node import Node, NavigationNode

# Playwright
from playwright.sync_api import sync_playwright, Browser, Page


class ScraperGraph:
    """TODO write class description"""
    def __init__(self):
        """TODO write method description"""
        self.nodes: dict[int, Node] = {}
        # TODO transform into something with faster lookup (e.g. dict, of ...), while still serializable
        self.edges: dict[int, list[int]] = defaultdict(list)

        # , play_wright_page: Page, result_object: any
        # self.page = play_wright_page
        # self.result_object = result_object

    def execute(self):
        """Execute the steps of the graph in a depth-first manner."""
        # Add the first node to the node stack, which will be executed first
        nodes_stack: list[Node] = [self.nodes[1]]

        # Execute the nodes in a depth-first manner
        while nodes_stack:
            node: Node = nodes_stack.pop()
            # Execute the node function with the inputs
            node_output: any = node()

            for child_id in self.edges[node.id]:
                child_node: Node = self.nodes[child_id]

                # Add the output of the node to the input of the children
                child_node.dynamic_inputs["output_previous_node"] = node_output

                nodes_stack.append(child_node)

    def add_node(self, node: Node):
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_edge(self, parent_node: Node, child_node: Node):
        """Add an edge to the graph."""
        self.edges[parent_node.id].append(child_node.id)

    def serialize(self):
        """Transform the graph to a dictionary representation."""
        return {
            "nodes": {i: node.serialize() for i, node in self.nodes.items()},
            "edges": self.edges
        }

    def save_to_file(self, file_path: str):
        """Save the graph to a file."""
        with open(file_path, "w") as file:
            json.dump(self.serialize(), file)

    def deserialize_node(self, node_dict: dict[str, any]) -> Node:
        """Compose a node from a dictionary representation."""
        if node_dict.get("node_type") == "navigation":
            node = NavigationNode.deserialize(node_dict)
            # node.page = self.page
            return node
        elif node_dict.get("node_type") == "regular":
            return Node.deserialize(node_dict)
        else:
            raise ValueError(f"Invalid node type: {node_dict.get('node_type')}")

    @classmethod
    def deserialize(cls, graph_dict: dict[str, any]) -> "ScraperGraph":
        """Compose a graph from a dictionary representation."""
        graph = cls()
        for node_dict in graph_dict["nodes"].values():
            node = Node.deserialize(node_dict)
            graph.add_node(node)
        # Transform the dict back to a default dict, ensuring that the keys are integers
        graph.edges = defaultdict(list, {int(k): v for k, v in graph_dict["edges"].items()})
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
    node1 = Node(id=1, function=pass_through, static_inputs={})
    node2 = NavigationNode(id=2, function=pass_through, static_inputs={})
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge(node1, node2)

    # Save the graph to a file
    graph.save_to_file("graph.json")
    graph_from_file = ScraperGraph.from_file("graph.json")

    print(graph.serialize())
    print(graph_from_file.serialize())

    # Check if the graph is the same
    assert graph.serialize() == graph_from_file.serialize()
    print("Graph saved and loaded successfully.")

    graph_from_file.execute()

