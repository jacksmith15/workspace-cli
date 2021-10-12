from tests.cli.commands.helpers import WORKSPACE_ROOT, run


class TestSync:
    @staticmethod
    def should_do_nothing_when_no_projects_are_configured():
        # GIVEN I have no projects configured
        # WHEN I workspace run a command
        result = run(["workspace", "sync"])
        # THEN I should see the expected output
        assert "No projects selected" in result.text

    @staticmethod
    def should_sync_dependencies_in_target_project():
        # GIVEN I have a project
        path = "libs/my-library"
        run(["workspace", "new", "--type", "poetry", path])
        # WHEN I run workspace sync on that project
        run(["workspace", "sync", "my-library"])
        # THEN the command should succeed
        # AND that project should now have a venv
        venv_path = WORKSPACE_ROOT / path / ".venv"
        assert venv_path.exists()
        assert venv_path.is_dir()
