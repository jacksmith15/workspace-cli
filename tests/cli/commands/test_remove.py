from tests.cli.commands.helpers import WORKSPACE_ROOT, run


class TestRemove:
    @staticmethod
    def should_remove_specified_project():
        # GIVEN a project is being tracked
        path = "libs/my-library"
        run(["workspace", "new", "--type", "poetry", path])
        # WHEN I remove the project
        run(["workspace", "remove", "my-library"])
        # THEN the project should no longer be tracked
        assert run(["workspace", "list", "--output", "names"]).text == ""
        # AND the project should still exist
        assert (WORKSPACE_ROOT / path).exists()

    @staticmethod
    def should_delete_when_flag_is_set():
        # GIVEN a project is being tracked
        path = "libs/my-library"
        run(["workspace", "new", "--type", "poetry", path])
        # WHEN I remove the project
        run(["workspace", "remove", "my-library", "--delete"])
        # THEN the project should no longer be tracked
        assert run(["workspace", "list", "--output", "names"]).text == ""
        # AND the project should still exist
        assert not (WORKSPACE_ROOT / path).exists()

    @staticmethod
    def should_warn_when_the_specified_workspace_does_not_match():
        # WHEN I remove a project which is not tracked
        result = run(["workspace", "remove", "my-library"])
        # THEN the exit code is 0
        assert result.returncode == 0
        # AND the expected warning message is displayed
        assert "No projects selected" in result.text
