import pytest

from tests.cli.commands.helpers import run


class TestWorkspacesReverse:
    @staticmethod
    def should_show_nothing_when_no_paths_are_provided():
        # GIVEN I have a workspace
        path = "libs/my-library"
        run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I run workspace reverse with no arguments
        result = run(["workspaces", "reverse"])
        # THEN there should be no output
        assert not result.text

    @staticmethod
    def should_show_matching_project_when_path_is_provided():
        # GIVEN I have a workspace
        path = "libs/my-library"
        run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I run workspace reverse with a file inside that workspace
        result = run(["workspaces", "reverse", "libs/my-library/foo"])
        # THEN there should be no output
        assert set(result.text.splitlines()) == {"my-library"}

    @staticmethod
    def should_differentiate_between_nested_projects():
        # GIVEN I have a workspace
        outer_path = "libs/my-library"
        run(["workspaces", "new", "--type", "poetry", outer_path])
        # AND a workspace nested inside it
        inner_path = "libs/my-library/other"
        run(["workspaces", "new", "--type", "poetry", inner_path])
        # WHEN I run workspace reverse with a file inside the inner project
        result = run(["workspaces", "reverse", f"{inner_path}/bar"])
        # THEN only the inner workspace should be shown
        assert set(result.text.splitlines()) == {"other"}

    @staticmethod
    @pytest.mark.parametrize("output", ["lines", "csv"])
    def should_detect_multiple_files_from_multiple_projects(output: str):
        # GIVEN I have three workspaces
        target_paths = {"libs/library-two", "libs/library-one"}
        paths = target_paths | {"libs/library-three"}
        for path in paths:
            run(["workspaces", "new", "--type", "poetry", path])
        # WHEN I run workspaces reverse with files from two of them
        args = [f"{target_path}/{foo}" for foo in ["foo", "bar"] for target_path in target_paths] + ["not-in-workspace"]
        result = run(["workspaces", "reverse", "--output", output, *args])
        if output == "csv":
            result_set = set(result.text.split(","))
        else:
            result_set = set(result.text.splitlines())
        assert result_set == {"library-one", "library-two"}
