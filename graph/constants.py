# Node functions
from node_functions.flow_control_functions import pass_through

# Result objects
from graph.result_dataclasses.company import Company


# Mapping of node names to the executable functions
NODE_NAME_TO_FUNCTION_MAP: dict[str, callable] = {
    pass_through.__name__: pass_through
}


# Mapping of result object names to the respective dataclasses
RESULT_OBJECT_NAME_TO_DATACLASS_MAP: dict[str, callable] = {
    Company.__name__: Company,
    None: None
}
