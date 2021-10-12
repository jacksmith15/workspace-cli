from __future__ import annotations

import shlex
import subprocess
from typing import TYPE_CHECKING, ClassVar, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from pathlib import Path  # pragma: no cover

    from workspace.core.models import Project  # pragma: no cover


class Adapter:
    name: ClassVar[Optional[str]]
    command_prefix: ClassVar[List[str]]

    def __init_subclass__(cls, *, name: str = None, command_prefix: Tuple[str, ...] = None):
        cls.name = name
        cls.command_prefix = list(command_prefix or [])

    def __init__(self, project: Project):
        self._project = project

    def __repr__(self):
        return f"{type(self)}({self._project})"

    def run(self, command: str, capture_output: bool = False, check: bool = False) -> subprocess.CompletedProcess:
        """Run a command within the project environment."""
        with self.popen(command, capture_output=capture_output) as process:
            try:
                stdout, stderr = process.communicate()
            except:
                process.kill()
                raise
            returncode = process.returncode
        result: subprocess.CompletedProcess = subprocess.CompletedProcess(
            command,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        )
        if check:
            result.check_returncode()
        return result

    def popen(self, command: str, capture_output: bool = True) -> subprocess.Popen:
        """Open a subprocess and return it."""
        command, kwargs = self.run_args(command)
        if capture_output:
            kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return subprocess.Popen(command, **kwargs)

    def run_args(self, command: str) -> Tuple[str, dict]:
        """Get modified command and kwargs that should be used when running inside the project.

        These arguments are passed directly to subprocess.Popen.
        """
        # We don't do shlex.join(prefix + shlex.split(command)) because this will escape e.g. |
        command = " ".join([shlex.join(self.command_prefix), command])
        return command, dict(cwd=self._project.resolved_path, shell=True)

    def dependencies(self, include_dev: bool = True) -> Set[str]:
        """Return the names of projects this project depends on."""
        raise NotImplementedError  # pragma: no cover

    def validate(self):
        """Validate the project.

        Implementations of this method should raise WorkspacesWorkspaceError if the
        project fails validation.
        """
        raise NotImplementedError  # pragma: no cover

    def sync(self, include_dev: bool = True) -> subprocess.CompletedProcess:
        """Sync dependencies of the project.

        This should preferably be a reproducible action (i.e. installing from a lockfile).
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def new(cls, path: Path):
        """Create a new project at path using default template.

        If an Adapter chooses not to implement this method, the user will be required to
        provide a custom template to initialise a project with this type.
        """
        raise NotImplementedError
