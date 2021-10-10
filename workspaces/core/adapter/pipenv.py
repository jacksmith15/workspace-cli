from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Set, Tuple

import pipenv
from pipfile import Pipfile

from workspaces.core.adapter.base import Adapter
from workspaces.core.exceptions import WorkspacesError, WorkspacesWorkspaceImproperlyConfigured

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
            raise WorkspacesWorkspaceImproperlyConfigured(f"No Pipfile found in workspace {self._workspace.name!r}.")
        try:
            _ = self.pipfile
        except Exception as exc:
            raise WorkspacesWorkspaceImproperlyConfigured(
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

    def run_args(self, command: str) -> Tuple[str, dict]:
        """Override args for running commands.

        Set PIPENV_IGNORE_VIRTUALENVS to prevent pipenv using the wrong venv
        in the case that workspaces is installed with a venv.
        """
        command, kwargs = super().run_args(command)

        env = os.environ.copy()
        env["PIPENV_IGNORE_VIRTUALENVS"] = "1"
        kwargs["env"] = env

        return command, kwargs

    @classmethod
    def new(cls, path: Path):
        try:
            from cookiecutter.main import cookiecutter
        except ImportError:
            raise WorkspacesError("Cookiecutter is not installed - run 'pip install workspaces[cookiecutter]'.")
        template_path = Path(__file__).parent.parent.parent / "templates/pipenv"
        try:
            version = sys.version_info
            cookiecutter(
                template=str(template_path),
                output_dir=path.parent,
                extra_context={"project_slug": path.name, "python_version": f"{version.major}.{version.minor}"},
                no_input=True,
            )
        except Exception as exc:
            raise WorkspacesError(
                f"""Failed to initialise pipenv workspace at {str(path)!r}:
  {str(exc)}
"""
            )
