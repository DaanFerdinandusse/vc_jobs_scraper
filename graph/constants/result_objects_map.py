# Standard
from typing import Any

# Result objects
from graph.result_dataclasses.company import Company

# Mapping of result object names to the respective dataclasses
RESULT_OBJECT_NAME_TO_DATACLASS_MAP: dict[str | None, Any] = {
    Company.__name__: Company,
    None: None
}
