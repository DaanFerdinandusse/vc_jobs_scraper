# Standard
from typing import Callable

# Node functions
from graph.node_functions.flow_control import pass_through, add_result_object_to_context
from graph.node_functions.navigation import navigate_to_url

# Mapping of node names to the executable functions
NODE_NAME_TO_FUNCTION_MAP: dict[str, Callable] = {
    pass_through.__name__: pass_through,
    add_result_object_to_context.__name__: add_result_object_to_context,
    navigate_to_url.__name__: navigate_to_url,
}
