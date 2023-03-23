import datetime
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Feature:
    """Class representing feature data."""

    name: str
    active: bool
    deadline: datetime.date | None = None
    ref: str | None = None

    def __eq__(self, other) -> bool:
        """Override to compare only by name."""
        if not isinstance(other, Feature):
            return NotImplemented
        return self.name == other.name
