import json
import os
import subprocess

import pytest

from tests.cli.commands.helpers import WORKSPACE_ROOT, run
from workspace.core.models import Workspace


class TestNew:
    @staticmethod
    def should_create_new_poetry_project_at_given_path():
        # WHEN I create a new project at a given path
        project_relpath = "libs/my-library"
        project_path = WORKSPACE_ROOT / project_relpath
        run(["workspace", "new", "--type", "poetry", project_relpath])
        # THEN the path should be a directory
        assert project_path.exists()
        # AND should contain a valid poetry project
        run(["poetry", "check"], cwd=project_path)
        # AND the poetry project should have the correct name
        assert run(["poetry", "version"], cwd=project_path).text == "my-library 0.1.0"
        # AND the new project should be tracked as a project in the workspace
        assert run(["workspace", "list", "--output", "names"]).text == "my-library"

    @staticmethod
    def should_fail_when_project_with_that_name_already_exists():
        # GIVEN a project is already tracked
        run(["workspace", "new", "--type", "poetry", "libs/my-library"])
        # WHEN I create a new project with the same name
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "new", "--type", "poetry", "other/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Project my-library already exists.")

    @staticmethod
    def should_fail_when_project_at_that_path_is_already_tracked():
        # GIVEN a project is already tracked
        run(["workspace", "new", "--type", "poetry", "libs/my-library"])
        # WHEN I try to create that project again
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "new", "--type", "poetry", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Path libs/my-library already tracked as project my-library")

    @staticmethod
    def should_fail_when_directory_already_exists():
        # GIVEN that a path exists
        os.makedirs(WORKSPACE_ROOT / "libs/my-library")
        # WHEN I try to create a project at that path
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "new", "--type", "poetry", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Path libs/my-library already exists")

    @staticmethod
    def should_fail_when_neither_type_nor_template_are_specified():
        # WHEN I run new without specifying type or template
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "new", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Must specify at least one of --type and --template options.")

    @staticmethod
    def should_create_project_from_template():
        # GIVEN a template is available
        template_path = "templates"
        run(["workspace", "template", "path", "add", template_path])
        # WHEN I run new using a template
        with subprocess.Popen(
            ["workspace", "new", "--template", "valid-pipenv-template", "libs/my-library"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=WORKSPACE_ROOT,
        ) as popen:
            # THEN the user is asked for template options excluding the directory name
            prompts = [
                ("project_name [My Library]:", "My Library"),
                ("package_name [my_library]:", "my_library"),
                ("python_version:", "3.8"),
            ]
            for expected_prompt, response in prompts:
                actual_prompt = popen.stdout.read1().decode().strip()
                while not actual_prompt:
                    actual_prompt = popen.stdout.read1().decode().strip()
                assert actual_prompt == expected_prompt
                popen.stdin.write((response + "\n").encode("utf-8"))
                popen.stdin.flush()
            output = popen.communicate()[0].decode().strip()
            # AND the exit code is 0
            assert popen.returncode == 0, output

        # AND the expected message is displayed
        assert output == "Created new project my-library at libs/my-library."
        # AND the project is created with detected type
        workspace = Workspace.from_path(WORKSPACE_ROOT)
        assert workspace.projects["my-library"].type == "pipenv"

        # AND additional context about the project was available to the template
        context = json.loads((WORKSPACE_ROOT / "libs/my-library/context.json").read_text())
        assert context == {
            "path": "libs/my-library",
            "name": "my-library",
        }

    @staticmethod
    def should_fail_when_non_existing_template_is_specified():
        # GIVEN a template path is set
        template_path = "templates"
        run(["workspace", "template", "path", "add", template_path])
        # WHEN I run new using a template which doesn't exist
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "new", "--template", "not-a-template", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Unknown template not-a-template.")

    @staticmethod
    def should_fail_when_template_type_is_not_detectable():
        # GIVEN a template path is set
        template_path = "templates"
        run(["workspace", "template", "path", "add", template_path])
        # WHEN I run new using a template which doesn't exist
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "new", "--template", "bad-template", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Could not detect type of generated project.")
        # AND the rendered template is removed
        assert not (WORKSPACE_ROOT / "libs/my-library").exists()

    @staticmethod
    def should_fail_if_type_has_no_default_template():
        # GIVEN a type adapter plugin without a default template is installed
        run(["workspace", "plugin", "add", "plugins.test_plugins"])
        custom_type = "custom-no-default-template"
        # WHEN I run new using that type
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspace", "new", "--type", custom_type, "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith(f"Type {custom_type} does not have a default template."), exc.text
