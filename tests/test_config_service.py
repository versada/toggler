"""Test class for configs merging functionality."""
from datetime import date

from toggler.services.config import load_configs, merge_configs


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


def test_01_load_configs():
    # GIVEN
    # WHEN
    configs = load_configs([CFG_STREAM_1, CFG_STREAM_2])
    # THEN
    assert len(configs) == 2
    cfg_1, cfg_2 = configs
    # CFG 1
    assert len(cfg_1) == 3
    assert cfg_1["feature1"]["modes"] == ["prod", "stage"]
    assert cfg_1["feature1"]["date"] == date(2023, 1, 1)
    assert len(cfg_1["feature1"]) == 4
    # CFG 2
    assert len(cfg_2) == 3
    assert len(cfg_2["feature1"]) == 1
    assert cfg_2["feature4"]["date"] == date(2023, 1, 1)


def test_02_merge_configs():
    # GIVEN
    configs = load_configs([CFG_STREAM_1, CFG_STREAM_2])
    # WHEN
    cfg = merge_configs(configs)
    # THEN
    assert len(cfg) == 4
    f1 = cfg["feature1"]
    assert len(f1) == 4
    assert f1["modes"] == ["prod", "stage"]
    assert f1["date"] == date(2023, 2, 2)
    assert f1["days_to_expire"] == 10
    f2 = cfg["feature2"]
    assert len(f2) == 3
    assert f2["modes"] == ["prod"]
    assert f2["date"] == date(2023, 1, 1)
    assert f2["ref"] == "r222"
    f3 = cfg["feature3"]
    assert f3["modes"] == ["other"]
    assert f3["date"] == date(2023, 1, 1)
    f4 = cfg["feature4"]
    assert f4["modes"] == ["stage"]
    assert f4["date"] == date(2023, 1, 1)
