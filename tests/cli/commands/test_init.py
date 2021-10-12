import subprocess

import pytest

from tests.cli.commands.helpers import WORKSPACE_ROOT, run
from workspace.core.models import Workspace


class TestInit:
    @staticmethod
    def should_create_workspace_file():
        # WHEN I run workspaces init
        # (init already runs in autouse fixture)
        # THEN a valid workspace file is created
        workspace = Workspace.from_path(WORKSPACE_ROOT)
        assert workspace.path == WORKSPACE_ROOT

    @staticmethod
    def should_fail_to_create_if_already_exists():
        # GIVEN a workspace has already been initialised at path
        # (init already runs in autouse fixture)
        # WHEN I attempt to init a workspace at the same path
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "init", "--path", WORKSPACE_ROOT], assert_success=False)
        exc = exc_info.value

        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith(f"File already exists at {WORKSPACE_ROOT}/workspace.json.")
