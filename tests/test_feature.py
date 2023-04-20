"""Test class for feature toggling functionality."""
import pathlib
from datetime import date

from toggler.toggler import Toggler
from toggler.services.env import (
    toggle_feature,
    modified_environ,
    ENV_KEY_CFG,
    ENV_KEY_MODE,
)

CFG_STREAM_1 = """---
feature1:
  modes: [prod, stage]
  date: 2023-01-01
  days_to_expire: 10
  ref: r123
feature2:
  modes: [stage]
  date: 2023-01-01
feature3:
  modes: [other]
  date: 2023-01-01
"""
CFG_STREAM_2 = """---
feature1:
  date: 2023-02-02
feature2:
  modes: [prod]
  ref: r222
feature4:
  modes: [stage]
  date: 2023-01-01
"""

path_cfg_1 = path = pathlib.Path(__file__).parent / "data/cfg_1.yml"


def test_01_prod_mode():
    # GIVEN
    # WHEN
    tog = Toggler("prod", paths=[path_cfg_1])
    # THEN
    assert len(tog.cfg) == 3
    assert tog.is_active("feature1") is True
    assert tog.is_active("feature2") is False
    assert tog.is_active("feature3") is False
    assert tog.is_active("feature4") is None
    expired_features = tog.check_deadlines()
    assert len(expired_features) == 1
    assert expired_features[0].name == "feature1"


def test_02_stage_mode():
    # GIVEN
    # WHEN
    tog = Toggler("stage", streams=[CFG_STREAM_1])
    # THEN
    assert len(tog.cfg) == 3
    assert tog.is_active("feature1") is True
    assert tog.is_active("feature2") is True
    assert tog.is_active("feature3") is False
    # WHEN
    feature1 = tog.cfg.get("feature1")
    # THEN
    assert feature1 is not None
    assert feature1.ref == "r123"
    assert feature1.deadline == date(2023, 1, 11)
    # WHEN
    feature2 = tog.cfg.get("feature2")
    assert feature2 is not None
    assert feature2.ref is None
    assert feature2.deadline is None
    # assert tog.mode_features["feature1"].ref == "r123"
    # assert tog.mode_features["feature2"].ref is None
    # 2023-01-01 + 10 days
    # assert tog.mode_features["feature1"].deadline == date(2023, 1, 11)
    # assert tog.mode_features["feature2"].deadline is None
    expired_features = tog.check_deadlines()
    assert len(expired_features) == 1
    assert expired_features[0].name == "feature1"


def test_03_forced_feature_via_env_prod():
    # GIVEN
    envs = {ENV_KEY_CFG: str(path_cfg_1), ENV_KEY_MODE: "prod"}
    with modified_environ(**envs):
        tog = Toggler()
    # WHEN
    with toggle_feature("feature3", True):
        # THEN
        assert tog.is_active("feature3") is True
    assert tog.is_active("feature3") is False
    # WHEN
    with toggle_feature("feature4", True):
        # THEN
        assert tog.is_active("feature4") is True
    assert tog.is_active("feature4") is None


def test_04_forced_feature_via_env_stage():
    # GIVEN
    tog = Toggler("stage", streams=[CFG_STREAM_1])
    # WHEN
    with toggle_feature("feature1", False):
        # THEN
        assert tog.is_active("feature1") is False
    assert tog.is_active("feature1") is True
    # GIVEN
    # WHEN
    with toggle_feature("feature3", True):
        # THEN
        assert tog.is_active("feature3") is True
    assert tog.is_active("feature3") is False


def test_05_feature_not_exists():
    tog = Toggler("stage", streams=[CFG_STREAM_1])
    assert tog.is_active("ff1122312312312") is None


def test_06_feature_prod_multiple_configs():
    tog = Toggler("prod", streams=[CFG_STREAM_1, CFG_STREAM_2])
    assert tog.is_active("feature1") is True
    assert tog.is_active("feature2") is True
    assert tog.is_active("feature3") is False
    assert tog.is_active("feature4") is False


def test_07_feature_stage_multiple_configs():
    tog = Toggler("stage", streams=[CFG_STREAM_1, CFG_STREAM_2])
    assert tog.is_active("feature1") is True
    assert tog.is_active("feature2") is False
    assert tog.is_active("feature3") is False
    assert tog.is_active("feature4") is True
