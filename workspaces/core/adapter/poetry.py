from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional, Set

from poetry.core.factory import Factory
from poetry.core.pyproject.exceptions import PyProjectException
from poetry.core.pyproject.toml import PyProjectTOML

from workspaces.core.adapter.base import Adapter
from workspaces.core.exceptions import WorkspaceImproperlyConfigured, WorkspacesError


class PoetryAdapter(Adapter, name="poetry", command_prefix=("poetry", "run")):
    @property
    def pyproject_path(self) -> Path:
        return self._workspace.resolved_path / "pyproject.toml"

    @property
    def pyproject(self) -> PyProjectTOML:
        return PyProjectTOML(path=self.pyproject_path)

    def dependencies(self, include_dev: bool = True) -> Set[str]:
        self.validate()
        pyproject = self.pyproject.file.read()
        dependencies = pyproject["tool"]["poetry"]["dependencies"]

        results = set()
        sections = ["dependencies"]
        if include_dev:
            sections.append("dev-dependencies")
        for section in sections:
            for key, value in dependencies.items():
                if isinstance(value, dict) and "path" in value:
                    path = (self._workspace.resolved_path / Path(value["path"])).resolve()
                    workspace = self._workspace.root.get_workspace_by_path(path)
                    if workspace:
                        results.add(workspace.name)
        return results

    def validate(self):
        if not (self.pyproject_path.exists() and self.pyproject_path.is_file()):
            raise WorkspaceImproperlyConfigured(f"No pyproject.toml found in workspace {self._workspace.name!r}.")
        error_message: Optional[str] = None
        try:
            local_config = self.pyproject.poetry_config
        except PyProjectException as exc:
            error_message = "  - {}\n".format(str(exc))
        else:
            check_result = Factory.validate(local_config)
            if check_result["errors"]:
                error_message = ""
                for error in check_result["errors"]:
                    error_message += "  - {}\n".format(error)

        if error_message:
            raise WorkspaceImproperlyConfigured(
                f"The Poetry configuration at {self.pyproject_path} is invalid:\n" + error_message
            )

    def sync(self, include_dev: bool = True) -> subprocess.CompletedProcess:
        """Sync dependencies of the workspace."""
        command = "poetry install".split(" ")
        if not include_dev:
            command.append("--no-dev")
        return subprocess.run(
            command,
            capture_output=False,
            check=False,
            cwd=self._workspace.resolved_path,
        )

    @classmethod
    def new(cls, path: Path):
        try:
            subprocess.run(
                f"poetry new {path.resolve()}".split(" "),
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            output = "\n  ".join([exc.stdout.decode().strip(), exc.stderr.decode().strip()]).strip()
            raise WorkspacesError(
                f"""Failed to initialise poetry workspace at {str(path)!r}:
  {output}
"""
            )
