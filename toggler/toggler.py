"""Module to manage Feature Flags configuration."""
from collections import defaultdict
import yaml

from io import FileIO
import pathlib
import os
import ast
import logging
import datetime


from .feature import Feature
from .env import form_feature_env_key, ENV_KEY_CFG
from .exceptions import MissingFeatureError

_logger = logging.getLogger(__name__)


def _load_cfg(
    stream: str | bytes | FileIO | None = None,
    path: str | pathlib.Path | None = None,
) -> dict:
    if stream is not None:
        return yaml.safe_load(stream)
    if path is not None:
        with open(path) as f:
            return yaml.safe_load(f)
    path_cfg = os.environ.get(ENV_KEY_CFG)
    if path_cfg:
        with open(path_cfg) as f:
            return yaml.safe_load(f)
    raise ValueError(
        f"To initiate Toggler, either stream, path or {ENV_KEY_CFG}"
        + " environ must be specified to load configuration!"
    )


class Toggler:
    """Class to parse feature flags configuration file for environment."""

    def __init__(
        self,
        mode: str | None = None,
        stream: str | bytes | FileIO | None = None,
        path: str | pathlib.Path | None = None,
        check_deadlines: bool = True,
    ):
        self._mode = self._prepare_mode(mode)
        self._cfg = _load_cfg(stream=stream, path=path)
        self._features_cfg = self._parse_cfg()
        if check_deadlines:
            self.check_deadlines()

    @property
    def features_cfg(self) -> dict[str, dict[str, Feature]]:
        return self._features_cfg

    @property
    def mode_features(self) -> dict[str, Feature]:
        """Return features for current mode."""
        return self.features_cfg[self.mode]

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
        feature = self.mode_features.get(name)
        if feature is None:
            try:
                # We now look if such feature exists in any of modes, to
                # inform about it.
                self._search_feature(name)
            except MissingFeatureError as e:
                _logger.warning(e.args[0])
            return None
        return feature.active

    def check_deadlines(self) -> list[Feature]:
        """Check if any feature is passed deadline.

        Returns:
            features that have expired.

        """
        today = datetime.date.today()
        expired = []
        for cfg_values in self.features_cfg.values():
            for feature in cfg_values.values():
                if feature.deadline and feature.deadline <= today:
                    logging.warning(
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
            mode = os.environ.get(ENV_KEY_CFG)
        if not mode:
            raise ValueError(
                "To initialize Toggler, you need to specify `mode` "
                + f"via __init__ or via {ENV_KEY_CFG} environment key"
            )
        return mode

    def _search_feature(
        self, name: str, mode: str | None = None, raise_not_found=True
    ) -> Feature | None:
        """Search feature via modes.

        Args:
            name: feature name
            mode: mode to search in. If not specified, will search through
                all modes, returning first found result.
            raise_not_found: whether to raise exception if Feature is
                not found.

        """
        if mode is not None:
            try:
                return self.features_cfg[mode][name]
            except KeyError:
                if raise_not_found:
                    raise MissingFeatureError(
                        f"Feature with name '{name}' in mode '{mode}', does not exist"
                    )
                return None
        for feature_data in self.features_cfg.values():
            feature = feature_data.get(name)
            if feature is not None:
                return feature
        if raise_not_found:
            raise MissingFeatureError(
                f"No feature found with name '{name}' in any of modes!"
            )
        return None

    def _is_active_via_env(self, name: str) -> bool | None:
        key = form_feature_env_key(name)
        if key in os.environ:
            return ast.literal_eval(os.environ[key])
        return None

    def _parse_feature_data(self, name: str, data: dict) -> Feature:
        return Feature(name=name, **data)

    def _parse_cfg(self) -> dict[str, dict[str, Feature]]:
        data = defaultdict(dict)
        for mode, mode_data in self._cfg.items():
            for name, feature_data in mode_data.items():
                data[mode][name] = self._parse_feature_data(name, feature_data)
        return data
