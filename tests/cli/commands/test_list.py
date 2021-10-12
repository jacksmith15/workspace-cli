import json

from tests.cli.commands.constants import WORKSPACE_ROOT
from tests.cli.commands.helpers import run


class TestList:
    @staticmethod
    def should_show_nothing_when_no_projects_are_configured():
        result = run(["workspace", "list"])
        assert result.stdout == ""

    @staticmethod
    def should_show_workspaces():
        # GIVEN I have two projects
        paths = {"libs/my-library", "libs/my-other-library"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # WHEN I run workspace list
        result = run(["workspace", "list"])
        # THEN the projects should be shown
        assert (
            result.stdout
            == f"""
Name: my-library
Type: poetry
Path: {WORKSPACE_ROOT / "libs/my-library"}
Dependencies: []

Name: my-other-library
Type: poetry
Path: {WORKSPACE_ROOT / "libs/my-other-library"}
Dependencies: []
"""
        )

    @staticmethod
    def should_show_workspace_names():
        # GIVEN I have two projects
        paths = {"libs/my-library", "libs/my-other-library"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # WHEN I run workspace list
        result = run(["workspace", "list", "--output=names"])
        # THEN the projects should be shown
        assert set(result.text.splitlines()) == {"my-library", "my-other-library"}

    @staticmethod
    def should_show_targets_only_if_specified():
        # GIVEN I have two projects
        paths = {"libs/my-library", "libs/my-other-library"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # WHEN I run workspace list
        result = run(["workspace", "list", "--output=names", "my-library"])
        # THEN the projects should be shown
        assert set(result.text.splitlines()) == {"my-library"}

    @staticmethod
    def should_output_to_json():
        # GIVEN I have two projects
        paths = {"libs/my-library", "libs/my-other-library"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND one projects depends on the other
        run(["poetry", "add", "../my-other-library"], cwd="libs/my-library")
        # WHEN I run workspace list with json output
        output = run(["workspace", "list", "--output", "json"]).text
        # THEN each output line should be valid json
        result = [json.loads(line) for line in output.splitlines()]
        # AND the result should contain the expected information
        assert result == [
            {
                "name": "my-library",
                "type": "poetry",
                "path": str(WORKSPACE_ROOT / "libs/my-library"),
                "depends_on": ["my-other-library"],
            },
            {
                "name": "my-other-library",
                "type": "poetry",
                "path": str(WORKSPACE_ROOT / "libs/my-other-library"),
                "depends_on": [],
            },
        ]
