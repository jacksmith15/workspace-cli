from types import MappingProxyType
from typing import Type

from workspaces.core.adapter.base import Adapter
from workspaces.core.exceptions import WorkspaceImproperlyConfigured

try:
    from workspaces.core.adapter.pipenv import PipenvAdapter

    assert PipenvAdapter
except ImportError:
    pass  # pragma: no cover

try:
    from workspaces.core.adapter.poetry import PoetryAdapter

    assert PoetryAdapter
except ImportError:
    pass  # pragma: no cover


__all__ = [
    "Adapter",
    "get_adapter",
]


def get_adapter(name: str) -> Type[Adapter]:
    adapters = get_adapters()
    try:
        return adapters[name]
    except KeyError:
        raise WorkspaceImproperlyConfigured(
            f"No adapter of type {name!r} registered. Available types are {list(adapters)}."
        )


def get_adapters() -> MappingProxyType:
    return MappingProxyType(
        {
            subclass.name: subclass
            for subclass in _all_subclasses(Adapter)
            if hasattr(subclass, "name") and subclass.name
        }
    )


def _all_subclasses(cls: Type):
    """Get all explicit and implicit subclasses of a type."""
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in _all_subclasses(c)])
