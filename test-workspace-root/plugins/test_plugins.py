"""Test plugin module containing simple adapters."""
import os
from pathlib import Path
from typing import Set

from workspace.core.adapter import Adapter


class CustomAdapterNoDefaultTemplate(Adapter, name="custom-no-default-template"):
    def dependencies(self, include_dev: bool = True) -> Set[str]:
        return set()

    def validate(self):
        assert (self._project.resolved_path / "custom").exists()

    def sync(self):
        return


class CustomAdapter(CustomAdapterNoDefaultTemplate, name="custom"):
    @classmethod
    def new(cls, path: Path):
        os.makedirs(path)
        with open(path / "custom", "w", encoding="utf-8") as file:
            file.write("custom")
