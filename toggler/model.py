import datetime
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Feature:
    """Class representing feature data."""

    name: str
    active: bool
    date: datetime.date
    deadline: datetime.date | None = None
    ref: str | None = None

    def __eq__(self, other) -> bool:
        """Override to compare only by name."""
        if not isinstance(other, Feature):
            return NotImplemented
        return self.name == other.name

    @classmethod
    def from_feature_dict(cls, mode: str, name: str, data: dict):
        """Parse feature data coming from configuration."""
        feature_data = dict(data)
        active = mode in feature_data.pop("modes")
        days_to_expire = feature_data.pop("days_to_expire", None)
        if days_to_expire is not None:
            dt = feature_data["date"]
            feature_data["deadline"] = dt + datetime.timedelta(days=days_to_expire)
        return Feature(name=name, active=active, **feature_data)
