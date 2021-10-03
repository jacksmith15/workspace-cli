import subprocess
from pathlib import Path

import pytest

from tests.cli.commands.helpers import PROJECT_ROOT, run


class TestWorkspaceRun:
    @staticmethod
    def should_show_nothing_when_no_workspaces_are_configured():
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
        output = {str(Path(line).relative_to(PROJECT_ROOT)) for line in result.stdout.decode().strip().splitlines()}
        assert output == paths

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
            ]
        )
        # THEN I should get the expected result
        output = {str(Path(line).relative_to(PROJECT_ROOT)) for line in result.stdout.decode().strip().splitlines()}
        assert output == target_paths

    @staticmethod
    def should_fail_if_command_fails():
        # GIVEN I have two workspaces
        paths = {"libs/library-one", "libs/library-two"}
        for path in paths:
            run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I run a command with exit code 2 in the first workspace
        Path(PROJECT_ROOT / "libs/library-two" / "foo").touch()
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "run", "ls", "foo"])
        exc = exc_info.value
        # THEN the exit code is 2
        assert exc.returncode == 2
        # AND the output second command still ran
        assert "Running ls foo in libs/library-two" in exc.stderr.decode()
