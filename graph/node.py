# Standard
import logging
from dataclasses import dataclass

# Node functions
from graph.node_name_to_function_map import NODE_NAME_TO_FUNCTION_MAP


@dataclass
class Node:
    """TODO class description"""
    id: int
    function: callable
    input: dict[str, any]

    def serialize(self):
        """Transform the node to a dictionary representation."""
        return {
            "id": self.id,
            "function": self.function.__name__,
            "input": self.input
        }

    @classmethod
    def deserialize(cls, node_dict: dict[str, any]):
        """Compose a node from a dictionary representation."""
        return cls(
            id=node_dict["id"],
            function=NODE_NAME_TO_FUNCTION_MAP[node_dict["function"]],
            input=node_dict["input"]
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
