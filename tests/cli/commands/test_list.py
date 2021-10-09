import json

from tests.cli.commands.constants import PROJECT_ROOT
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

    @staticmethod
    def should_output_to_json():
        # GIVEN I have two workspaces
        paths = {"libs/my-library", "libs/my-other-library"}
        for path in paths:
            run(["workspaces", "new", "--type", "poetry", path])
        # AND one workspaces depends on the other
        run(["poetry", "add", "../my-other-library"], cwd="libs/my-library")
        # WHEN I run workspace list with json output
        output = run(["workspaces", "list", "--output", "json"]).text
        # THEN each output line should be valid json
        result = [json.loads(line) for line in output.splitlines()]
        # AND the result should contain the expected information
        assert result == [
            {
                "name": "my-library",
                "type": "poetry",
                "path": str(PROJECT_ROOT / "libs/my-library"),
                "depends_on": ["my-other-library"],
            },
            {
                "name": "my-other-library",
                "type": "poetry",
                "path": str(PROJECT_ROOT / "libs/my-other-library"),
                "depends_on": [],
            },
        ]
