# Standard
import logging

# Constants
from graph.constants.result_objects_map import RESULT_OBJECT_NAME_TO_DATACLASS_MAP


def pass_through(**kwargs) -> None:
    """Simply pass through function for testing."""
    pass


def add_result_object_to_context(node, result_object: str, **kwargs) -> None:
    """Add the result object to the context of the node."""
    node.context["result_object"] = RESULT_OBJECT_NAME_TO_DATACLASS_MAP[result_object]()


if __name__ == "__main__":
    from graph.node import Node
    from graph.result_dataclasses.company import Company
    logging.basicConfig(level=logging.INFO)

    pass_through()

    node = Node(id="1", function=pass_through, static_inputs={})
    add_result_object_to_context(node, Company.__name__)
    print(node.context)
