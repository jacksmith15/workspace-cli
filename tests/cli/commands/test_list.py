from tests.cli.commands.helpers import run


class TestWorkspaceList:
    @staticmethod
    def should_show_nothing_when_no_workspaces_are_configured():
        result = run(["workspaces", "list"])
        assert result.text == ""
