import os
import subprocess

import pytest

from tests.cli.commands.helpers import PROJECT_ROOT, run
from workspaces.core.models import WorkspacesProject


class TestWorkspacesNew:
    @staticmethod
    def should_create_new_poetry_workspace_at_given_path():
        # WHEN I create a new workspace at a given path
        workspace_relpath = "libs/my-library"
        workspace_path = PROJECT_ROOT / workspace_relpath
        run(["workspaces", "new", "--type", "poetry", workspace_relpath])
        # THEN the path should be a directory
        assert workspace_path.exists()
        # AND should contain a valid poetry project
        run(["poetry", "check"], cwd=workspace_path)
        # AND the poetry project should have the correct name
        assert run(["poetry", "version"], cwd=workspace_path).text == "my-library 0.1.0"
        # AND the new project should be tracked as a workspace in the root project
        assert run(["workspaces", "list"]).text == "my-library"

    @staticmethod
    def should_fail_when_project_with_that_name_already_exists():
        # GIVEN a project is already tracked
        run(["workspaces", "new", "--type", "poetry", "libs/my-library"])
        # WHEN I create a new workspace with the same name
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "new", "--type", "poetry", "other/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Workspace my-library already exists.")

    @staticmethod
    def should_fail_when_project_at_that_path_is_already_tracked():
        # GIVEN a project is already tracked
        run(["workspaces", "new", "--type", "poetry", "libs/my-library"])
        # WHEN I try to create that workspace again
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "new", "--type", "poetry", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Path libs/my-library already tracked as workspace my-library")

    @staticmethod
    def should_fail_when_directory_already_exists():
        # GIVEN that a path exists
        os.makedirs(PROJECT_ROOT / "libs/my-library")
        # WHEN I try to create a workspace at that path
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "new", "--type", "poetry", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Path libs/my-library already exists")

    @staticmethod
    def should_fail_when_neither_type_nor_template_are_specified():
        # WHEN I run new without specifying type or template
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "new", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Must specify at least one of --type and --template options.")

    @staticmethod
    def should_create_workspace_from_template():
        # GIVEN a template is available
        template_path = "templates"
        run(["workspaces", "template", "path", "add", template_path])
        # WHEN I run new using a template
        with subprocess.Popen(
            ["workspaces", "new", "--template", "valid-pipenv-template", "libs/my-library"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=PROJECT_ROOT,
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
            assert popen.returncode == 0

        # AND the expected message is displayed
        assert output == "Created new workspace my-library at libs/my-library."
        # AND the workspace is created with detected type
        project = WorkspacesProject.from_path(PROJECT_ROOT)
        assert project.workspaces["my-library"].type == "pipenv"

    @staticmethod
    def should_fail_when_non_existing_template_is_specified():
        # GIVEN a template path is set
        template_path = "templates"
        run(["workspaces", "template", "path", "add", template_path])
        # WHEN I run new using a template which doesn't exist
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "new", "--template", "not-a-template", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Unknown template not-a-template.")

    @staticmethod
    def should_fail_when_template_type_is_not_detectable():
        # GIVEN a template path is set
        template_path = "templates"
        run(["workspaces", "template", "path", "add", template_path])
        # WHEN I run new using a template which doesn't exist
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "new", "--template", "bad-template", "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith("Could not detect type of generated project.")
        # AND the rendered template is removed
        assert not (PROJECT_ROOT / "libs/my-library").exists()

    @staticmethod
    def should_fail_if_type_has_no_default_template():
        # GIVEN a type adapter plugin without a default template is installed
        run(["workspaces", "plugin", "add", "plugins.test_plugins"])
        custom_type = "custom-no-default-template"
        # WHEN I run new using that type
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["workspaces", "new", "--type", custom_type, "libs/my-library"], assert_success=False)
        exc = exc_info.value
        # THEN the exit code is 1
        assert exc.returncode == 1
        # AND the expected error message is displayed
        assert exc.text.startswith(f"Type {custom_type} does not have a default template."), exc.text
