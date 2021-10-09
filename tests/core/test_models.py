import json
import os
import shutil
from pathlib import Path
from typing import Union

import pytest

from tests.utils import override_settings
from workspaces.core.exceptions import (
    WorkspacesPluginError,
    WorkspacesProjectNotFoundError,
    WorkspacesProjectValidationError,
)
from workspaces.core.models import WorkspacesProject

ROOT_PATH = Path("test-tree").resolve()
PROJECT_FILENAME = "workspaces-test-project.json"


@pytest.fixture(autouse=True, scope="module")
def _override_project_filename():
    """Override filename to reduce chance of conflicts."""
    with override_settings(project_filename=PROJECT_FILENAME):
        yield


@pytest.fixture(autouse=True)
def root_path():
    os.mkdir(ROOT_PATH)
    try:
        yield ROOT_PATH
    finally:
        shutil.rmtree(ROOT_PATH)


def init_workspaces_file(path: Union[str, Path]):
    with open(Path(path) / PROJECT_FILENAME, "w", encoding="utf-8") as file:
        file.write(json.dumps({"workspaces": {}}))


class TestWorkspacesProject:
    @staticmethod
    def should_detect_workspace_given_exact_path():
        # GIVEN a path contains a workspaces config file
        init_workspaces_file(ROOT_PATH)
        # WHEN I load the project with exact filepath
        project = WorkspacesProject.from_path(ROOT_PATH / PROJECT_FILENAME)
        # THEN the project is loaded
        assert project.path == ROOT_PATH

    @staticmethod
    def should_detect_workspace_given_root_directory():
        # GIVEN a path contains a workspaces config file
        init_workspaces_file(ROOT_PATH)
        # WHEN I load the project with directory path
        project = WorkspacesProject.from_path(ROOT_PATH)
        # THEN the project is loaded
        assert project.path == ROOT_PATH

    @staticmethod
    def should_detect_workspace_given_child_directory():
        # GIVEN a path contains a workspaces config file
        init_workspaces_file(ROOT_PATH)
        # WHEN I load the project from a child directory
        child_dir = ROOT_PATH / "child"
        os.mkdir(child_dir)
        project = WorkspacesProject.from_path(child_dir)
        # THEN the project is loaded
        assert project.path == ROOT_PATH

    @staticmethod
    def should_detect_nearest_workspace_when_multiple_are_available():
        # GIVEN a path contains a workspaces config file
        init_workspaces_file(ROOT_PATH)
        # AND a child directory also contains a workspaces config file
        child_dir = ROOT_PATH / "child"
        os.mkdir(child_dir)
        init_workspaces_file(child_dir)
        # WHEN I load the project from the child directory
        project = WorkspacesProject.from_path(child_dir)
        # THEN the child project is loaded
        assert project.path == child_dir

    @staticmethod
    def should_raise_when_no_workspace_found():
        # GIVEN a directory contains no workspaces config file
        path = ROOT_PATH
        # WHEN I load the project from that directory
        with pytest.raises(WorkspacesProjectNotFoundError) as exc_info:
            WorkspacesProject.from_path(ROOT_PATH)
        exc = exc_info.value
        # THEN the correct error is raised
        assert str(exc) == f"No workspaces project file '{PROJECT_FILENAME}' found in '{path}' or its parents."

    @staticmethod
    @pytest.mark.parametrize("workspace_content", ["{}", "..."])
    def should_raise_on_invalid_workspace(workspace_content: str):
        # GIVEN a directory contains an invalid workspaces config file
        with open(ROOT_PATH / PROJECT_FILENAME, "w", encoding="utf-8") as file:
            file.write(workspace_content)
        # WHEN I load the project from that directory
        with pytest.raises(WorkspacesProjectValidationError):
            WorkspacesProject.from_path(ROOT_PATH)
        # THEN the correct exception is raised

    @staticmethod
    def should_raise_on_invalid_plugin():
        # GIVEN a directory contains a workspaces config file with invalid plugin
        with open(ROOT_PATH / PROJECT_FILENAME, "w", encoding="utf-8") as file:
            file.write(json.dumps({"workspaces": {}, "plugins": ["foo.bar"]}))
        # WHEN I load the project from that directory
        with pytest.raises(WorkspacesPluginError):
            WorkspacesProject.from_path(ROOT_PATH)
        # THEN the correct exception is raised
