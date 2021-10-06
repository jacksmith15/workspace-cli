from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, ClassVar, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from pathlib import Path  # pragma: no cover

    from workspaces.core.models import Workspace  # pragma: no cover


class Adapter:
    name: ClassVar[Optional[str]]
    command_prefix: ClassVar[List[str]]

    def __init_subclass__(cls, *, name: str = None, command_prefix: Tuple[str, ...] = None):
        cls.name = name
        cls.command_prefix = list(command_prefix or [])

    def __init__(self, workspace: Workspace):
        self._workspace = workspace

    def __repr__(self):
        return f"{type(self)}({self._workspace})"

    def run(self, command: List[str], capture_output: bool = False, check: bool = False) -> subprocess.CompletedProcess:
        """Run a command within the workspace."""
        return subprocess.run(
            self.command_prefix + command,
            capture_output=capture_output,
            check=check,
            cwd=self._workspace.resolved_path,
        )

    def dependencies(self, include_dev: bool = True) -> Set[str]:
        """Return the names of workspaces this workspace depends on."""
        raise NotImplementedError  # pragma: no cover

    def validate(self):
        """Validate the workspace."""
        raise NotImplementedError  # pragma: no cover

    def sync(self, include_dev: bool = True) -> subprocess.CompletedProcess:
        """Sync dependencies of the workspace."""
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def new(cls, path: Path):
        raise NotImplementedError
