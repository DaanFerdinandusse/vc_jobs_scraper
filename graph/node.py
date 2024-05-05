# Standard
import logging
from dataclasses import dataclass, field
from typing import Callable, Any, Literal

# Node functions
from graph.constants import NODE_NAME_TO_FUNCTION_MAP


@dataclass
class Node:
    """
    The node class represents a single step in the scraping process. The node is executable with
    three types of inputs:
        - Static inputs: These are the configurations of the scraping step specified by the developer.
            (e.g., the URL to scrape, the CSS selector to use, etc.)
        - Dynamic inputs: These are the outputs of the previous nodes in the graph.
            (e.g. a specific element extracted from the HTML)
        - Shared inputs: These are objects shared between nodes managed by the scraping graph.
            (e.g. the browser, the result object, etc.)

    :param id: The unique identifier of the node.
    :param function: The function to execute when the node is called.
    :param static_inputs: Configuration of the scraping step.
    :param dynamic_inputs: Outputs of the previous nodes in the graph.
    :param shared_inputs: Inputs shared between nodes.
    :param node_type: The type of the node. (e.g. "regular", "navigation").
    """
    id: int
    function: Callable[..., Any]
    static_inputs: dict[str, any]
    dynamic_inputs: dict[str, any] = field(default_factory=dict)
    shared_inputs: dict[str, any] = field(default_factory=dict)
    node_type: Literal["regular", "navigation"] = field(default="regular")

    def __call__(self) -> Any:
        """Execute the function of the node."""
        function_inputs = {**self.static_inputs, **self.dynamic_inputs, **self.shared_inputs}
        return self.function(**function_inputs)

    def serialize(self) -> dict[str, Any]:
        """Transform the node to a dictionary representation. Only the static inputs are serialized."""
        return {
            "id": self.id,
            "function": self.function.__name__,
            "static_inputs": self.static_inputs,
            "node_type": self.node_type
        }

    @classmethod
    def deserialize(cls, node_dict: dict[str, Any]):
        """Compose a node from a dictionary representation."""
        return cls(
            id=node_dict["id"],
            function=NODE_NAME_TO_FUNCTION_MAP[node_dict["function"]],
            static_inputs=node_dict["static_inputs"],
            node_type=node_dict["node_type"],
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
