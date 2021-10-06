import subprocess
from pathlib import Path

import pytest

from tests.cli.commands.helpers import PROJECT_ROOT, run


class TestRun:
    @staticmethod
    def should_do_nothing_when_no_workspaces_are_configured():
        # GIVEN I have no workspaces configured
        # WHEN I workspace run a command
        result = run(["workspaces", "run", "pwd"])
        # THEN I should see the expected output
        assert "No workspaces selected" in result.text

    @staticmethod
    def should_run_in_each_workspace():
        # GIVEN I have two workspaces
        paths = {"libs/my-library", "libs/my-other-library"}
        for path in paths:
            run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I workspace run a command with no option
        result = run(["workspaces", "run", "pwd"])
        # THEN I should get the expected result
        output = set(result.stdout.decode().strip().splitlines())
        assert {str(PROJECT_ROOT / path) for path in paths} <= output

    @staticmethod
    def should_run_on_targets_only():
        # GIVEN I have three workspaces
        target_paths = {"libs/library-two", "libs/library-one"}
        paths = target_paths | {"libs/library-three"}
        for path in paths:
            run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I workspace run a command on target workspaces
        result = run(
            [
                "workspaces",
                "run",
                f"--targets={','.join([path.split('/')[-1] for path in target_paths])}",
                "--",
                "pwd",
            ],
            assert_success=True,
        )
        # THEN I should get the expected result
        output = set(result.stdout.decode().strip().splitlines())
        assert {str(PROJECT_ROOT / path) for path in target_paths} <= output

    @staticmethod
    def should_run_on_globbed_targets():
        # GIVEN I have workspaces with a common prefix
        library_paths = {"libs/library-one", "libs/library-two"}
        for path in library_paths:
            run(["workspaces", "new", "--type", "poetry", path])
        # AND other workspaces with a different prefix
        application_path = "apps/application-one"
        run(["workspaces", "new", "--type", "poetry", application_path])
        # WHEN I workspace run a command using a glob to select the common prefix
        result = run(["workspaces", "run", "--targets=library-*", "--", "pwd"])
        # THEN I the command should run in the matching workspaces
        output = set(result.stdout.decode().strip().splitlines())
        assert {str(PROJECT_ROOT / path) for path in library_paths} <= output
        assert str(PROJECT_ROOT / application_path) not in output

    @staticmethod
    def should_fail_if_command_fails():
        # GIVEN I have two workspaces
        paths = {"libs/library-one", "libs/library-two"}
        for path in paths:
            run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I run a command with exit code 2 in the first workspace
        Path(PROJECT_ROOT / "libs/library-two" / "foo").touch()
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "run", "ls", "foo"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 2
        assert exc.returncode == 2
        # AND the output second command still ran
        assert "Running ls foo in libs/library-two" in exc.stderr.decode()
