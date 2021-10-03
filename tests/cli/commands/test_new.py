import subprocess

import pytest

from tests.cli.commands.helpers import PROJECT_ROOT, run


class TestWorkspaceNew:
    @staticmethod
    def should_create_new_poetry_workspace_at_given_path():
        # WHEN I create a new workspace at a given path
        workspace_relpath = "libs/my-library"
        workspace_path = PROJECT_ROOT / workspace_relpath
        run(["workspaces", "new", "--type", "poetry", workspace_relpath])
        # THEN the path should be a directory
        assert workspace_path.exists()
        # AND should contain a valid poetry project
        run(["poetry", "check"], cwd=workspace_path)
        # AND the poetry project should have the correct name
        assert run(["poetry", "version"], cwd=workspace_path).text == "my-library 0.1.0"
        # AND the new project should be tracked as a workspace in the root project
        assert run(["workspaces", "list"]).text == "my-library"

    @staticmethod
    def should_fail_when_project_with_that_name_already_exists():
        # GIVEN a project is already tracked
        run(["workspaces", "new", "--type", "poetry", "libs/my-library"])
        # WHEN I create a new workspace with the same name
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "new", "--type", "poetry", "other/my-library"])
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Workspace my-library already exists.")
