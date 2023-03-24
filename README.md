# Toggler

Toggler allows to set up feature toggles (flags) on a YAML file and validate whether
specific flag is ON or OFF on specific environment.

## How to Use

### Configure Feature Toggles

Feature toggles are configured in `yaml` file:

```yaml
---
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
```

Structure:

* modes (e.g prod, stage), defines features defined on specific mode.
* features (e.g feature1, feature2) are feature names used to identify which
  feature is used or not:
    - active: whether feature is enabled or not. If feature is not defined on
      specific mode, it is implicitly treated as disabled. This is the only required field.
    - ref: reference to feature or ticket (for convenience).
    - deadline: if set, will check if feature flag has been for too long and logs
      a warning if its passed a deadline.

### Define mode and config file path

You can either explicitly initialize `Toggler` with its optional arguments, `mode` and `path` (or `stream`) or you can use environment variables `TOGGLER_MODE` and `TOGGLER_CFG`.

For example:

```
TOGGLER_MODE=prod TOGGLER_CFG=/path/to/tog.yml my-app
```

### Initialize `Toggler` and check features activity

```python
from toggler.toggler import Toggler

tog = Toggler()  # expecting specified env variables
if tog.is_active("feature1"):
    # feature1 logic
    ...
else:
    # old logic
    ...
```

### Using toggler in tests

You can force toggle feature to make it easier to test.

```python
from toggler.env import toggle_feature


def test_feature1_on():
    with toggle_feature("feature1", True):  # Force enable
        # test if feature1 logic works as expected
        ...


def test_feature1_off():
    with toggle_feature("feature1", False):  # Force disable
        # test if logic without feature1 works as expected
        ...
```
