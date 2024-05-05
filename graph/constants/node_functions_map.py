# Standard
from typing import Callable

# Node functions
from graph.node_functions.flow_control_functions import pass_through, add_result_object_to_context

# Mapping of node names to the executable functions
NODE_NAME_TO_FUNCTION_MAP: dict[str, Callable] = {
    pass_through.__name__: pass_through,
    add_result_object_to_context.__name__: add_result_object_to_context
}
