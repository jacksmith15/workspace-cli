import subprocess

import pytest

from tests.cli.commands.helpers import run


class TestTemplatePathAdd:
    @staticmethod
    def should_add_a_new_template_path():
        # GIVEN I have a directory containing templates
        template_path = "templates"
        # WHEN I add that path to the workspace
        result = run(["workspace", "template", "path", "add", template_path])
        # THEN the expected output should be seen
        assert result.text.startswith(f"Added {template_path} to available template directories.")

    @staticmethod
    def should_fail_if_path_already_added():
        # GIVEN a directory is already on the template path
        template_path = "templates"
        run(["workspace", "template", "path", "add", template_path])
        # WHEN I add that path to the project again
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "template", "path", "add", template_path], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith(f"Already configured to detect templates at {template_path}.")


class TestTemplatePathRemove:
    @staticmethod
    def should_fail_if_path_not_tracked():
        # GIVEN I have a directory containing templates which is not on the path
        template_path = "templates"
        # WHEN I remove that path from the project
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "template", "path", "remove", template_path], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith(f"Not configured to detect templates at {template_path}.")

    @staticmethod
    def should_remove_path_if_tracked():
        # GIVEN a directory is already on the template path
        template_path = "templates"
        run(["workspace", "template", "path", "add", template_path])
        # WHEN I remove that path from the project
        result = run(["workspace", "template", "path", "remove", template_path])
        # THEN the expected output should be seen
        assert result.text.startswith(f"Stopped detecting templates at {template_path}.")


class TestTemplateList:
    @staticmethod
    def should_show_nothing_when_template_path_not_set():
        # WHEN I run template list
        result = run(["workspace", "template", "list"])
        # THEN nothing should be shown
        assert not result.text

    @staticmethod
    def should_list_available_templates():
        # GIVEN I have a directory containing templates
        template_path = "templates"
        # AND that directory is on the template path
        run(["workspace", "template", "path", "add", template_path])
        # WHEN I run template list
        output = run(["workspace", "template", "list"]).text.splitlines()
        result = {name: path for line in output for name, path in [line.split(None, 1)]}
        # THEN the expected templates are included
        assert result["valid-pipenv-template"] == "templates/valid-pipenv-template"
        assert result["bad-template"] == "templates/bad-template"
        # AND nested templates are not included
        assert "other-valid-pipenv-template" not in result
        # AND only template directories are detected
        assert "not-a-template" not in result

    @staticmethod
    def should_resolve_paths_in_correct_order():
        # GIVEN I have two template paths with overlapping template names
        inner = "templates/nested"
        outer = "templates"
        run(["workspace", "template", "path", "add", inner])
        run(["workspace", "template", "path", "add", outer])
        # WHEN I list the templates
        output = run(["workspace", "template", "list"]).text.splitlines()
        result = {name: path for line in output for name, path in [line.split(None, 1)]}
        # THEN templates on both paths are shown
        assert set(result) == {"bad-template", "valid-pipenv-template", "other-valid-pipenv-template"}
        # AND the first path wins on conflicts
        assert result["valid-pipenv-template"] == "templates/nested/valid-pipenv-template"
