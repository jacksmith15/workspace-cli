import subprocess
from pathlib import Path

import pytest

from tests.cli.commands.helpers import WORKSPACE_ROOT, run


class TestRun:
    @staticmethod
    def should_do_nothing_when_no_projects_are_configured():
        # GIVEN I have no projects configured
        # WHEN I workspace run a command
        result = run(["workspace", "run", "-c", "pwd"])
        # THEN I should see the expected output
        assert "No projects selected" in result.text

    @staticmethod
    def should_run_in_each_workspace():
        # GIVEN I have two projects
        paths = {"libs/my-library", "libs/my-other-library"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # WHEN I workspace run a command with no option
        result = run(["workspace", "run", "-c", "pwd"])
        # THEN I should get the expected result
        output = set(result.stdout.strip().splitlines())
        assert {str(WORKSPACE_ROOT / path) for path in paths} <= output

    @staticmethod
    def should_run_on_targets_only():
        # GIVEN I have three projects
        target_paths = {"libs/library-two", "libs/library-one"}
        paths = target_paths | {"libs/library-three"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # WHEN I workspace run a command on target projects
        result = run(
            ["workspace", "run", "-c", "pwd", *[path.split("/")[-1] for path in target_paths]],
            assert_success=True,
        )
        # THEN I should get the expected result
        output = set(result.stdout.strip().splitlines())
        assert {str(WORKSPACE_ROOT / path) for path in target_paths} <= output

    @staticmethod
    def should_run_on_globbed_targets():
        # GIVEN I have projects with a common prefix
        library_paths = {"libs/library-one", "libs/library-two"}
        for path in library_paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND other projects with a different prefix
        application_path = "apps/application-one"
        run(["workspace", "new", "--type", "poetry", application_path])
        # WHEN I workspace run a command using a glob to select the common prefix
        result = run(["workspace", "run", "-c", "pwd", "library-*"])
        # THEN I the command should run in the matching projects
        output = set(result.stdout.strip().splitlines())
        assert {str(WORKSPACE_ROOT / path) for path in library_paths} <= output
        assert str(WORKSPACE_ROOT / application_path) not in output

    @staticmethod
    def should_fail_if_command_fails():
        # GIVEN I have two projects
        paths = {"libs/library-one", "libs/library-two"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # WHEN I run a command with exit code 2 in the first project
        Path(WORKSPACE_ROOT / "libs/library-two" / "foo").touch()
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "run", "-c", "ls foo"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 2
        assert exc.returncode == 2
        # AND the output shows that the second command still ran
        assert "Running ls foo  (library-two)" in exc.stderr

    @staticmethod
    def should_support_piping_inside_command():
        # GIVEN I have a project
        project = "library-one"
        run(["workspace", "new", "--type", "poetry", f"libs/{project}"])
        # WHEN I run a command with a pipe
        result = run(["workspace", "run", "-c", "echo foo | grep foo"])
        # THEN the expected output should be seen
        assert result.stdout.splitlines()[-1] == "foo"

    @staticmethod
    def should_support_running_in_parallel():
        # GIVEN I have two projects
        paths = {"libs/library-one", "libs/library-two"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND a command will succeed in one project and fail in the other
        Path(WORKSPACE_ROOT / "libs/library-two" / "foo").touch()
        command = ["workspace", "run", "-c", "ls foo", "--parallel"]

        # WHEN I run the command in parallel
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(command, assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 2
        assert exc.returncode == 2
