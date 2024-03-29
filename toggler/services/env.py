import contextlib
import os


ENV_KEY_CFG = "TOGGLER_CFG"
ENV_KEY_MODE = "TOGGLER_MODE"

# TODO: this helper could be used more generally than just for toggler.


@contextlib.contextmanager
def modified_environ(*remove, **update):  # Taken from: shorturl.at/ajEW2
    """Temporarily update the `os.environ` dictionary in-place.

    The `os.environ` dictionary is updated in-place so that the
    modification is sure to work in all situations.

    Args:
        remove: Environment variables to remove.
        update: Dictionary of environment variables and values to add/update.

    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]


def form_feature_env_key(name):
    return f"TOGGLER_FEATURE_{name}"


@contextlib.contextmanager
def toggle_feature(name: str, active: bool):
    """Temporarily toggle feature is_active value via environ.

    This is intended mostly for testing.
    """
    key = form_feature_env_key(name)
    with modified_environ(**{key: str(active)}):
        yield
