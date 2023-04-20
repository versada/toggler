"""Utilities to prepare configuration data for toggler."""

import os
import yaml
import mergedeep
from typing import MutableMapping

from ..types import OptionalStream, OptionalStreams, OptionalPath, OptionalPaths
from ..model import Feature
from .env import ENV_KEY_CFG

MERGE_STRAT = mergedeep.Strategy.REPLACE


def prepare_config(
    mode: str, streams: OptionalStreams = None, paths: OptionalPaths = None
):
    """Prepare config to be used for toggler.

    1. Configurations are loaded from streams or paths.
    2. If there are multiple configs, they are merged into one. Order
        is important. Last in order configs overwrite data.
    3. Merged raw configuration is parsed into configuration with features
        activity per specified mode.
    """
    configs = load_configs(streams, paths)
    config = merge_configs(configs)
    return parse_config(mode, config)


def load_configs(
    streams: OptionalStreams = None, paths: OptionalPaths = None
) -> list[dict]:
    configs = []
    args = _prepare_multi_load_cfg_args(streams, paths)
    for kwargs in args:
        configs.append(_load_config(**kwargs))
    return configs


def merge_configs(configs: list[dict]) -> MutableMapping:
    if not configs:
        return {}
    main_cfg, other_configs = configs[0], configs[1:]
    return mergedeep.merge(main_cfg, *other_configs, strategy=MERGE_STRAT)


def parse_config(mode: str, config: dict | MutableMapping) -> dict[str, Feature]:
    cfg = {}
    for name, feature_data in config.items():
        cfg[name] = Feature.from_feature_dict(mode, name, feature_data)
    return cfg


def _prepare_multi_load_cfg_args(
    streams: OptionalStreams = None, paths: OptionalPaths = None
) -> list[dict]:
    if streams:
        return [{"stream": stream} for stream in streams]
    if paths:
        return [{"path": path} for path in paths]
    path_cfg = os.environ.get(ENV_KEY_CFG)
    if path_cfg:
        return [{"path": p.strip()} for p in path_cfg.split(",")]
    raise ValueError(
        f"To initiate Toggler Configuration, either stream, path or {ENV_KEY_CFG}"
        + " environ must be specified to load configuration!"
    )


def _load_config(
    stream: OptionalStream = None,
    path: OptionalPath = None,
) -> dict:
    if stream is not None:
        return yaml.safe_load(stream)
    if path is not None:
        with open(path) as f:
            return yaml.safe_load(f)
    return {}
