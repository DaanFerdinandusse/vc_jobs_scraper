# Standard
import json
import logging
from typing import Any
from collections import defaultdict

# Node dataclasses
from graph.node import Node

# Result objects
from graph.result_dataclasses.company import Company

# Playwright
from playwright.sync_api import sync_playwright, Browser, Page


class ScraperGraph:
    """
    Class representing a graph of nodes. Each node is an executable step in the scraping process.
    The graph is executed in a depth-first manner, passing the output of each node to its children.
    """
    def __init__(self, page_driver: Page, start_node_id: str = "1"):
        """Initializes an empty graph. Nodes and edges are stored as dictionaries."""
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, list[str]] = defaultdict(list)

        self.start_node_id = start_node_id
        self.page_driver = page_driver

    def execute(self):
        """
        Execute the steps of the graph in a depth-first manner. Each node is executed once,
        passing the output to its children. Additionally, the context of a node is passed to its children.
        This ensures that once a context like the result object is set, it is available to all children.
        """
        # Add the first node to the node stack, which will be executed first
        nodes_stack: list[Node] = [self.nodes[self.start_node_id]]

        # Execute the nodes in a depth-first manner
        while nodes_stack:
            node: Node = nodes_stack.pop()
            # Execute the node function with the inputs
            node_output: Any = node()

            for child_id in self.edges[node.id]:
                child_node: Node = self.nodes[child_id]

                # Add the output of the node to the input of the children
                child_node.dynamic_inputs["output_previous_node"] = node_output
                child_node.context = node.context

                nodes_stack.append(child_node)

    def add_node(self, node: Node):
        """Add a node to the graph."""
        node.context["page_driver"] = self.page_driver
        self.nodes[node.id] = node

    def add_edge(self, parent_node: Node, child_node: Node):
        """Add an edge to the graph."""
        self.edges[parent_node.id].append(child_node.id)

    def serialize(self) -> dict[str, Any]:
        """Transform the graph to a dictionary representation."""
        return {
            "start_node_id": self.start_node_id,
            "nodes": {i: node.serialize() for i, node in self.nodes.items()},
            "edges": self.edges,
        }

    def save_to_file(self, file_path: str):
        """Save the graph to a file."""
        with open(file_path, "w") as file:
            json.dump(self.serialize(), file)

    @classmethod
    def deserialize(cls, graph_dict: dict[str, Any], page_driver: Page) -> "ScraperGraph":
        """Compose a graph from a dictionary representation."""
        graph = cls(page_driver=page_driver)
        for node_dict in graph_dict["nodes"].values():
            node = Node.deserialize(node_dict)
            graph.add_node(node)

        graph.edges = defaultdict(list, graph_dict["edges"])
        graph.start_node_id = graph_dict["start_node_id"]

        return graph


def scraper_graph_from_file(file_path: str, page_driver: Page) -> "ScraperGraph":
    """
    Create a graph from a file.

    :param file_path: The path to the file to load the graph configuration from.
    :param page_driver: Playwright page object for interactions with the websites.
    :return: The graph object.
    """
    with open(file_path, "r") as file:
        graph_dict = json.load(file)
    return ScraperGraph.deserialize(graph_dict, page_driver)


if __name__ == "__main__":
    from node_functions.flow_control_functions import pass_through, add_result_object_to_context
    logging.basicConfig(level=logging.INFO)

    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        page: Page = browser.new_page()

        # Create a graph
        graph = ScraperGraph(page_driver=page)
        node1 = Node(id="1", function=pass_through, static_inputs={})
        node2 = Node(id="2", function=add_result_object_to_context, static_inputs={"result_object": Company.__name__})
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge(node1, node2)

        # Save the graph to a file
        graph.save_to_file("graph.json")
        graph_from_file = scraper_graph_from_file("graph.json", page)

        print(graph.serialize())
        print(graph_from_file.serialize())

        # Check if the graph is the same
        assert graph.serialize() == graph_from_file.serialize()
        print("Graph saved and loaded successfully.")

        graph_from_file.execute()

