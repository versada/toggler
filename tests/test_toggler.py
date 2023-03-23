"""Test class for feature toggling functionality."""
import pathlib
from datetime import date

from toggler.toggler import Toggler
from toggler.env import toggle_feature, modified_environ, ENV_KEY_CFG, ENV_KEY_MODE

CFG_STREAM_1 = """---
prod:
  feature2:
    active: true
stage:
  feature1:
    active: true
    ref: r123
    deadline: 2022-01-01
  feature2:
    active: true
  feature3:
    active: false
"""

path_cfg_1 = path = pathlib.Path(__file__).parent / "data/cfg_1.yml"


def test_01_prod_mode():
    # GIVEN
    # WHEN
    tog = Toggler("prod", path=path_cfg_1)
    # THEN
    assert len(tog.features_cfg) == 2
    assert len(tog.mode_features) == 1
    assert tog.is_active("feature1") is None
    assert tog.is_active("feature2") is True
    assert tog.is_active("feature3") is None
    expired_features = tog.check_deadlines()
    assert len(expired_features) == 1
    assert expired_features[0].name == "feature1"


def test_02_stage_mode():
    # GIVEN
    # WHEN
    tog = Toggler("stage", stream=CFG_STREAM_1)
    # THEN
    assert len(tog.features_cfg) == 2
    assert len(tog.mode_features) == 3
    assert tog.is_active("feature1") is True
    assert tog.is_active("feature2") is True
    assert tog.is_active("feature3") is False
    assert tog.mode_features["feature1"].ref == "r123"
    assert tog.mode_features["feature2"].ref is None
    assert tog.mode_features["feature1"].deadline == date(2022, 1, 1)
    assert tog.mode_features["feature2"].deadline is None
    expired_features = tog.check_deadlines()
    assert len(expired_features) == 1
    assert expired_features[0].name == "feature1"


def test_03_forced_feature_via_env_prod():
    # GIVEN
    envs = {ENV_KEY_CFG: str(path_cfg_1), ENV_KEY_MODE: "prod"}
    with modified_environ(**envs):
        tog = Toggler()
    # WHEN
    with toggle_feature("feature1", True):
        # THEN
        assert tog.is_active("feature1") is True
    assert tog.is_active("feature1") is None


def test_04_forced_feature_via_env_stage():
    # GIVEN
    tog = Toggler("stage", stream=CFG_STREAM_1)
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
    tog = Toggler("stage", stream=CFG_STREAM_1)
    assert tog.is_active("ff1122312312312") is None
