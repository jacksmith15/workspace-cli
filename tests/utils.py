from contextlib import contextmanager
from dataclasses import replace

from workspace.core.settings import get_settings


@contextmanager
def override_settings(**kwargs):
    settings = get_settings()
    # Validate:
    replace(settings, **kwargs)

    original = dict(settings.__dict__)
    try:
        settings.__dict__.update(kwargs)
        yield
    finally:
        settings.__dict__ = original
