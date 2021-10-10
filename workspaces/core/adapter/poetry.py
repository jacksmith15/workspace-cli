from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Set, Tuple

from poetry.core.factory import Factory
from poetry.core.pyproject.exceptions import PyProjectException
from poetry.core.pyproject.toml import PyProjectTOML

from workspaces.core.adapter.base import Adapter
from workspaces.core.exceptions import WorkspacesError, WorkspacesWorkspaceImproperlyConfigured


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
            raise WorkspacesWorkspaceImproperlyConfigured(
                f"No pyproject.toml found in workspace {self._workspace.name!r}."
            )
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
            raise WorkspacesWorkspaceImproperlyConfigured(
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

    def run_args(self, command: str) -> Tuple[str, dict]:
        """Get modified command and kwargs that should be used when running inside the workspace.

        Deactivate any active virtual environments when running commands in the workspace,
        otherwise poetry will use that instead of managing its own.
        """
        command, kwargs = super().run_args(command)

        env = os.environ.copy()
        venv_path = env.get("VIRTUAL_ENV", None)
        if not venv_path:
            return command, kwargs

        del env["VIRTUAL_ENV"]
        env["PATH"] = ":".join([path for path in env.get("PATH", "").split(":") if path != f"{venv_path}/bin"])
        kwargs["env"] = env
        return command, kwargs

    @classmethod
    def new(cls, path: Path):
        try:
            from cookiecutter.main import cookiecutter
        except ImportError:
            raise WorkspacesError("Cookiecutter is not installed - run 'pip install workspaces[cookiecutter]'.")
        template_path = Path(__file__).parent.parent.parent / "templates/poetry"
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
                f"""Failed to initialise poetry workspace at {str(path)!r}:
  {str(exc)}
"""
            )
