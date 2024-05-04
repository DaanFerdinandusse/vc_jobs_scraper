from node_functions.flow_control_functions import pass_through


# Mapping of node names to the executable functions
NODE_NAME_TO_FUNCTION_MAP: dict[str, callable] = {
    pass_through.__name__: pass_through
}
