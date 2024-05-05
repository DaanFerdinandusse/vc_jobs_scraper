# Standard
import logging
from dataclasses import dataclass, field

# Node functions
from graph.node_name_to_function_map import NODE_NAME_TO_FUNCTION_MAP


@dataclass
class Node:
    """TODO class description"""
    id: int
    function: callable
    static_inputs: dict[str, any]
    node_type: str = field(default="regular")
    dynamic_inputs: dict[str, any] = field(default_factory=dict)
    shared_inputs: dict[str, any] = field(default_factory=dict)

    def __call__(self):
        """Execute the function of the node."""
        function_inputs = {**self.static_inputs, **self.dynamic_inputs, **self.shared_inputs}
        return self.function(**function_inputs)

    def serialize(self):
        """Transform the node to a dictionary representation. Only the static inputs are serialized."""
        return {
            "id": self.id,
            "function": self.function.__name__,
            "static_inputs": self.static_inputs,
            "node_type": self.node_type
        }

    @classmethod
    def deserialize(cls, node_dict: dict[str, any]):
        """Compose a node from a dictionary representation."""
        return cls(
            id=node_dict["id"],
            function=NODE_NAME_TO_FUNCTION_MAP[node_dict["function"]],
            static_inputs=node_dict["static_inputs"],
            node_type=node_dict["node_type"],
        )


class NavigationNode(Node):
    """TODO class description"""
    node_type: str = field(default="navigation")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
