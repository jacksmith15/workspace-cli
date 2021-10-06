import subprocess

import pytest

from tests.cli.commands.helpers import PROJECT_ROOT, run
from workspaces.core.models import WorkspacesProject


class TestWorkspacesInit:
    @staticmethod
    def should_create_workspaces_file():
        # WHEN I run workspaces init
        # (init already runs in autouse fixture)
        # THEN a valid workspaces project file is created
        project = WorkspacesProject.from_path(PROJECT_ROOT)
        assert project.path == PROJECT_ROOT

    @staticmethod
    def should_fail_to_create_if_already_exists():
        # GIVEN a workspace has already been initialised at path
        # (init already runs in autouse fixture)
        # WHEN I attempt to init a project at the same path
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "init", "--path", PROJECT_ROOT], assert_success=False)
        exc = exc_info.value

        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith(f"File already exists at {PROJECT_ROOT}/workspaces.json.")
