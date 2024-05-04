# Standard
import logging
from dataclasses import dataclass


@dataclass
class Edge:
    """TODO class description"""
    source_id: int
    target_id: int
    use_output_as_input: bool

    def serialize(self):
        """Transform the edge to a dictionary representation."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "use_output_as_input": self.use_output_as_input
        }

    @classmethod
    def deserialize(cls, edge_dict: dict[str, any]):
        """Compose an edge from a dictionary representation."""
        return cls(
            source_id=edge_dict["source_id"],
            target_id=edge_dict["target_id"],
            use_output_as_input=edge_dict["use_output_as_input"]
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
