from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Set

import pipenv
from pipfile import Pipfile

from workspaces.core.adapter.base import Adapter
from workspaces.core.exceptions import WorkspaceImproperlyConfigured

assert pipenv  # please the linter - pipenv must be imported to access vendored pipfile.


class PipenvAdapter(Adapter, name="pipenv", command_prefix=("pipenv", "run")):
    @property
    def pipfile_path(self) -> Path:
        return self._workspace.resolved_path / "Pipfile"

    @property
    def pipfile(self):
        # pipfile is vendored by pipenv, so both imports are necessary.
        return Pipfile.load(self.pipfile_path)

    def dependencies(self, include_dev: bool = True) -> Set[str]:
        pipfile = self.pipfile
        sections = ["default"]
        if include_dev:
            sections.append("develop")
        results = set()
        for section in sections:
            for name, value in pipfile.data[section].items():
                if isinstance(value, dict) and "path" in value:
                    path = (self._workspace.resolved_path / Path(value["path"])).resolve()
                    workspace = self._workspace.root.get_workspace_by_path(path)
                    if workspace:
                        results.add(workspace.name)
        return results

    def validate(self):
        if not (self.pipfile_path.exists() and self.pipfile_path.is_file()):
            raise WorkspaceImproperlyConfigured(f"No Pipfile found in workspace {self._workspace.name!r}.")
        try:
            _ = self.pipfile
        except Exception as exc:
            raise WorkspaceImproperlyConfigured(
                f"Error loading pipfile for workspace {self._workspace.name!r}: {str(exc)}"
            )

    def sync(self, include_dev: bool = True) -> subprocess.CompletedProcess:
        """Sync dependencies of the workspace."""
        command = "pipenv sync".split(" ")
        if include_dev:
            command.append("--dev")
        return subprocess.run(
            command,
            capture_output=False,
            check=False,
            cwd=self._workspace.resolved_path,
        )
