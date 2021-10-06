import subprocess

import pytest

from tests.cli.commands.constants import PROJECT_ROOT
from tests.cli.commands.helpers import run


class TestPluginAdd:
    @staticmethod
    def should_add_a_new_plugin():
        # GIVEN a plugin is available on PYTHONPATH
        plugin = "plugins.test_plugins"
        # WHEN I add that plugin
        result = run(["workspaces", "plugin", "add", plugin])
        # THEN the expected output should be seen
        assert result.text.startswith(f"Added plugin {plugin}.")

    @staticmethod
    def should_fail_to_add_nonexistent_plugin():
        # GIVEN a plugin is not importable
        plugin = "foo.bar"
        # WHEN I add that plugin
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "plugin", "add", plugin], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith(f"Could not import plugin {plugin}.")

    @staticmethod
    def should_fail_if_plugin_already_added():
        # GIVEN a plugin is already added
        plugin = "plugins.test_plugins"
        run(["workspaces", "plugin", "add", plugin])
        # WHEN I add that plugin again
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "plugin", "add", plugin], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith(f"Plugin {plugin} already installed.")


class TestPluginRemove:
    @staticmethod
    def should_remove_plugin():
        # GIVEN a plugin is already added
        plugin = "plugins.test_plugins"
        run(["workspaces", "plugin", "add", plugin])
        # WHEN I remove that plugin
        result = run(["workspaces", "plugin", "remove", plugin])
        # THEN the expected output should be seen
        assert result.text.startswith(f"Removed plugin {plugin}.")

    @staticmethod
    def should_fail_if_plugin_not_installed():
        # GIVEN a plugin is not added
        plugin = "plugins.test_plugins"
        # WHEN I remove that plugin
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "plugin", "remove", plugin], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith(f"Plugin {plugin} not installed.")


class TestPluginList:
    @staticmethod
    def should_list_plugins():
        # GIVEN a plugin is already added
        plugin = "plugins.test_plugins"
        run(["workspaces", "plugin", "add", plugin])
        # WHEN I list plugins
        result = run(["workspaces", "plugin", "list"])
        # THEN the plugin should be in the output
        assert result.text.splitlines() == [plugin]


class TestPluginE2E:
    @staticmethod
    def should_use_plugins_in_workflow():
        run(["workspaces", "plugin", "add", "plugins.test_plugins"])
        run(["workspaces", "new", "--type", "custom", "libs/my-library"])
        assert (PROJECT_ROOT / "libs/my-library/custom").exists()
        run(["workspaces", "remove", "my-library"])
        run(["workspaces", "add", "--type", "custom", "libs/my-library"])
