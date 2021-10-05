import os
import subprocess

import pytest

from tests.cli.commands.helpers import PROJECT_ROOT, run


class TestWorkspacesAdd:
    @staticmethod
    def should_add_new_workspace_from_given_path():
        # GIVEN a poetry project exists at a given path
        workspace_relpath = "libs/my-library"
        run(["poetry", "new", workspace_relpath])
        # WHEN I add the path as a workspace
        run(["workspaces", "add", workspace_relpath])
        # THEN the project should now be tracked as a workspace in the root project
        assert run(["workspaces", "list"]).text == "my-library"

    @staticmethod
    def should_fail_when_project_with_that_name_already_exists():
        # GIVEN a project is already tracked
        run(["workspaces", "new", "libs/my-library", "--type", "poetry"])
        # AND another project exists with the same name
        run(["poetry", "new", "other/my-library"])
        # WHEN I attempt to add that project as a workspace
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "add", "other/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Workspace my-library already exists.")

    @staticmethod
    def should_fail_when_project_at_given_path_already_exists():
        # GIVEN a project is already tracked
        run(["workspaces", "new", "libs/my-library", "--type", "poetry"])
        # WHEN I attempt to add that project as a workspace
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "add", "libs/my-library", "--name", "my-library-alt"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1, exc.text
        # AND the expected error message is displayed
        assert exc.text.startswith("Path libs/my-library already tracked as workspace my-library."), exc.text

    @staticmethod
    def should_fail_when_type_is_invalid():
        # GIVEN a directory exists
        os.mkdir(PROJECT_ROOT / "foo")
        # WHEN I attempt to add it project with an unknown type
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "add", "foo", "--type", "notatype"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1, exc.text
        # AND the expected error message is displayed
        assert exc.text.startswith("No adapter of type 'notatype' registered.")

    @staticmethod
    def should_fail_when_type_is_unspecified_and_undetectable():
        # GIVEN an empty directory exists
        path = "foo"
        os.mkdir(PROJECT_ROOT / path)
        # WHEN I attempt to add it project without specifying a type
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "add", "foo"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1, exc.text
        # AND the expected error message is displayed
        assert exc.text.startswith(f"Could not detect type of project at path {path}")

    @staticmethod
    def should_fail_when_target_path_doesnt_exist():
        # WHEN I attempt to add a workspace from a path which does not exist
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "add", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 2
        assert exc.returncode == 2
        # AND the expected error message is displayed
        assert "Directory 'libs/my-library' does not exist" in exc.text

    @staticmethod
    def should_fail_when_pyproject_is_not_present():
        # GIVEN a directory exists but does not contain a pyproject.toml
        path = "libs/my-library"
        os.makedirs(PROJECT_ROOT / path)
        # WHEN I attempt to add that path as a workspace
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "add", "libs/my-library", "--type", "poetry"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert "No pyproject.toml found in workspace" in exc.text

    @staticmethod
    def should_fail_when_not_a_poetry_project():
        # GIVEN a directory contains an empty pyproject.toml
        path = "libs/my-library"
        os.makedirs(PROJECT_ROOT / path)
        (PROJECT_ROOT / path / "pyproject.toml").touch()
        # WHEN I attempt to add that path as a workspace
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "add", "libs/my-library", "--type", "poetry"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert "[tool.poetry] section not found" in exc.text, exc.text
