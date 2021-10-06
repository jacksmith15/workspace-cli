from tests.cli.commands.helpers import run


class TestList:
    @staticmethod
    def should_show_nothing_when_no_workspaces_are_configured():
        result = run(["workspaces", "list"])
        assert result.text == ""

    @staticmethod
    def should_show_workspaces_when_configured():
        # GIVEN I have two workspaces
        paths = {"libs/my-library", "libs/my-other-library"}
        for path in paths:
            run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I run workspace list
        result = run(["workspaces", "list"])
        # THEN the workspaces should be shown
        assert set(result.text.splitlines()) == {"my-library", "my-other-library"}
