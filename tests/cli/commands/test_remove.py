from tests.cli.commands.helpers import PROJECT_ROOT, run


class TestRemove:
    @staticmethod
    def should_remove_specified_workspace():
        # GIVEN a workspace is being tracked
        path = "libs/my-library"
        run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I remove the workspace
        run(["workspaces", "remove", "my-library"])
        # THEN the workspace should no longer be tracked
        assert run(["workspaces", "list", "--output", "names"]).text == ""
        # AND the project should still exist
        assert (PROJECT_ROOT / path).exists()

    @staticmethod
    def should_delete_when_flag_is_set():
        # GIVEN a workspace is being tracked
        path = "libs/my-library"
        run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I remove the workspace
        run(["workspaces", "remove", "my-library", "--delete"])
        # THEN the workspace should no longer be tracked
        assert run(["workspaces", "list", "--output", "names"]).text == ""
        # AND the project should still exist
        assert not (PROJECT_ROOT / path).exists()

    @staticmethod
    def should_warn_when_the_specified_workspace_does_not_match():
        # WHEN I remove a workspace which is not tracked
        result = run(["workspaces", "remove", "my-library"])
        # THEN the exit code is 0
        assert result.returncode == 0
        # AND the expected warning message is displayed
        assert "No workspaces selected" in result.text
