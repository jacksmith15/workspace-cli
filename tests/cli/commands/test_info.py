import json

import pytest

from tests.cli.commands.constants import WORKSPACE_ROOT
from tests.cli.commands.helpers import run


class TestInfo:
    @staticmethod
    @pytest.fixture(autouse=True)
    def setup():
        # GIVEN I have two projects
        paths = {"libs/my-library", "libs/my-other-library"}
        for path in paths:
            run(["workspace", "new", "--type", "poetry", path])
        # AND a plugin is enabled
        run(["workspace", "plugin", "add", "plugins.test_plugins"])
        # AND a template path is set
        run(["workspace", "template", "path", "add", "templates"])

    @staticmethod
    def should_display_default_output():
        # WHEN I get project info
        result = run(["workspace", "info"])
        # THEN the expected output should be seen
        assert (
            result.stdout
            == f"""
Path: {WORKSPACE_ROOT}
Projects:
    my-library        libs/my-library        (poetry)
    my-other-library  libs/my-other-library  (poetry)
Plugins:
    plugins.test_plugins
Template Path: [templates]

"""
        )

    @staticmethod
    def should_display_json_output():
        # WHEN I get project info as json
        output = run(["workspace", "info", "--output", "json"]).stdout
        # THEN the output should be valid json
        result = json.loads(output)
        # AND the result should contain the expected information
        assert result == {
            "path": str(WORKSPACE_ROOT),
            "projects": {
                "my-library": {"path": "libs/my-library", "type": "poetry"},
                "my-other-library": {"path": "libs/my-other-library", "type": "poetry"},
            },
            "plugins": ["plugins.test_plugins"],
            "template_path": ["templates"],
        }
