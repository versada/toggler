"""Module to manage Feature Flags configuration."""
import os
import ast
import logging
import datetime


from .model import Feature
from .types import OptionalStreams, OptionalPaths
from .services.env import form_feature_env_key, ENV_KEY_MODE
from .services.config import prepare_config

_logger = logging.getLogger(__name__)


class Toggler:
    """Class to parse feature flags configuration file for environment."""

    def __init__(
        self,
        mode: str | None = None,
        streams: OptionalStreams = None,
        paths: OptionalPaths = None,
        check_deadlines: bool = True,
    ):
        self._mode = self._prepare_mode(mode)
        self._cfg = prepare_config(self.mode, streams, paths)
        if check_deadlines:
            self.check_deadlines()

    @property
    def cfg(self) -> dict[str, Feature]:
        return self._cfg

    @property
    def mode(self) -> str:
        return self._mode

    def is_active(self, name: str) -> bool | None:
        """Check if current mode feature is enabled.

        If feature is not explicitly defined on current mode, None value
        is returned instead.
        """
        # Values coming from environ can temporary override existing
        # features, to make it more flexible!
        env_val = self._is_active_via_env(name)
        if env_val is not None:
            return env_val
        feature = self.cfg.get(name)
        if feature is None:
            _logger.warning(f"No feature found with name '{name}'")
            return None
        return feature.active

    def check_deadlines(self) -> list[Feature]:
        """Check if any feature is passed deadline.

        Returns:
            features that have expired.

        """
        today = datetime.date.today()
        expired = []
        for feature in self.cfg.values():
            if feature.deadline and feature.deadline <= today:
                _logger.warning(
                    'Feature Flag "%s" (reference: %s), '
                    + "with deadline %s, has expired. "
                    + "Consider removing this flag!",
                    feature.name,
                    feature.ref,
                    feature.deadline,
                )
                expired.append(feature)
        return expired

    def _prepare_mode(self, mode: str | None) -> str:
        if mode is None:
            mode = os.environ.get(ENV_KEY_MODE)
        if not mode:
            raise ValueError(
                "To initialize Toggler, you need to specify `mode` "
                + f"via __init__ or via {ENV_KEY_MODE} environment key"
            )
        return mode

    def _is_active_via_env(self, name: str) -> bool | None:
        key = form_feature_env_key(name)
        if key in os.environ:
            return ast.literal_eval(os.environ[key])
        return None
