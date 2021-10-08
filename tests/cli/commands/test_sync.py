from tests.cli.commands.helpers import PROJECT_ROOT, run


class TestSync:
    @staticmethod
    def should_do_nothing_when_no_workspaces_are_configured():
        # GIVEN I have no workspaces configured
        # WHEN I workspace run a command
        result = run(["workspaces", "sync"])
        # THEN I should see the expected output
        assert "No workspaces selected" in result.text

    @staticmethod
    def should_sync_dependencies_in_target_workspace():
        # GIVEN I have a workspace
        path = "libs/my-library"
        run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I run workspace sync on that workspace
        run(["workspaces", "sync", "my-library"])
        # THEN the command should succeed
        # AND that workspace should now have a venv
        venv_path = PROJECT_ROOT / path / ".venv"
        assert venv_path.exists()
        assert venv_path.is_dir()
