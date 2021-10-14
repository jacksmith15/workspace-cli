from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Set, Tuple

import pipenv
from pipfile import Pipfile

from workspace.core.adapter.base import Adapter
from workspace.core.exceptions import WorkspaceBaseError, WorkspaceProjectImproperlyConfigured

assert pipenv  # please the linter - pipenv must be imported to access vendored pipfile.


class PipenvAdapter(Adapter, name="pipenv", command_prefix=("pipenv", "run")):
    @property
    def pipfile_path(self) -> Path:
        return self._project.resolved_path / "Pipfile"

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
                    path = (self._project.resolved_path / Path(value["path"])).resolve()
                    project = self._project.root.get_project_by_path(path)
                    if project:
                        results.add(project.name)
        return results

    def validate(self):
        if not (self.pipfile_path.exists() and self.pipfile_path.is_file()):
            raise WorkspaceProjectImproperlyConfigured(f"No Pipfile found in project {self._project.name!r}.")
        try:
            _ = self.pipfile
        except Exception as exc:
            raise WorkspaceProjectImproperlyConfigured(
                f"Error loading pipfile for project {self._project.name!r}: {str(exc)}"
            )

    def sync_command(self, include_dev: bool = True) -> str:
        """Get the command which prepares the project environment."""
        command = "pipenv sync"
        if include_dev:
            command = command + " --dev"
        return command

    def run_args(self, command: str) -> Tuple[str, dict]:
        """Override args for running commands.

        Set PIPENV_IGNORE_VIRTUALENVS to prevent pipenv using the wrong venv in the case that workspace-cli is
        installed with a venv.
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
            raise WorkspaceBaseError("Cookiecutter is not installed - run 'pip install workspace-cli[cookiecutter]'.")
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
            raise WorkspaceBaseError(
                f"""Failed to initialise pipenv project at {str(path)!r}:
  {str(exc)}
"""
            )
