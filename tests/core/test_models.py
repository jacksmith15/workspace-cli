import json
import os
import shutil
from pathlib import Path
from typing import Union

import pytest

from tests.utils import override_settings
from workspace.core.exceptions import WorkspaceNotFoundError, WorkspacePluginError, WorkspaceValidationError
from workspace.core.models import Workspace

ROOT_PATH = Path("test-tree").resolve()
WORKSPACE_FILENAME = "workspace-test.json"


@pytest.fixture(autouse=True, scope="module")
def _override_filename():
    """Override filename to reduce chance of conflicts."""
    with override_settings(filename=WORKSPACE_FILENAME):
        yield


@pytest.fixture(autouse=True)
def root_path():
    os.mkdir(ROOT_PATH)
    try:
        yield ROOT_PATH
    finally:
        shutil.rmtree(ROOT_PATH)


def init_workspaces_file(path: Union[str, Path]):
    with open(Path(path) / WORKSPACE_FILENAME, "w", encoding="utf-8") as file:
        file.write(json.dumps({"projects": {}}))


class TestWorkspace:
    @staticmethod
    def should_detect_workspace_given_exact_path():
        # GIVEN a path contains a workspace file
        init_workspaces_file(ROOT_PATH)
        # WHEN I load the workspace with exact filepath
        workspace = Workspace.from_path(ROOT_PATH / WORKSPACE_FILENAME)
        # THEN the workspace is loaded
        assert workspace.path == ROOT_PATH

    @staticmethod
    def should_detect_workspace_given_root_directory():
        # GIVEN a path contains a workspace file
        init_workspaces_file(ROOT_PATH)
        # WHEN I load the workspace with directory path
        workspace = Workspace.from_path(ROOT_PATH)
        # THEN the workspace is loaded
        assert workspace.path == ROOT_PATH

    @staticmethod
    def should_detect_workspace_given_child_directory():
        # GIVEN a path contains a workspace file
        init_workspaces_file(ROOT_PATH)
        # WHEN I load the workspace from a child directory
        child_dir = ROOT_PATH / "child"
        os.mkdir(child_dir)
        workspace = Workspace.from_path(child_dir)
        # THEN the workspace is loaded
        assert workspace.path == ROOT_PATH

    @staticmethod
    def should_detect_nearest_workspace_when_multiple_are_available():
        # GIVEN a path contains a workspace file
        init_workspaces_file(ROOT_PATH)
        # AND a child directory also contains a workspace file
        child_dir = ROOT_PATH / "child"
        os.mkdir(child_dir)
        init_workspaces_file(child_dir)
        # WHEN I load the workspace from the child directory
        workspace = Workspace.from_path(child_dir)
        # THEN the child workspace is loaded
        assert workspace.path == child_dir

    @staticmethod
    def should_raise_when_no_workspace_found():
        # GIVEN a directory contains no workspace file
        path = ROOT_PATH
        # WHEN I load the workspace from that directory
        with pytest.raises(WorkspaceNotFoundError) as exc_info:
            Workspace.from_path(ROOT_PATH)
        exc = exc_info.value
        # THEN the correct error is raised
        assert str(exc) == f"No workspace file '{WORKSPACE_FILENAME}' found in '{path}' or its parents."

    @staticmethod
    @pytest.mark.parametrize("workspace_content", ["{}", "..."])
    def should_raise_on_invalid_workspace(workspace_content: str):
        # GIVEN a directory contains an invalid workspace file
        with open(ROOT_PATH / WORKSPACE_FILENAME, "w", encoding="utf-8") as file:
            file.write(workspace_content)
        # WHEN I load the workspace from that directory
        with pytest.raises(WorkspaceValidationError):
            Workspace.from_path(ROOT_PATH)
        # THEN the correct exception is raised

    @staticmethod
    def should_raise_on_invalid_plugin():
        # GIVEN a directory contains a workspace file with invalid plugin
        with open(ROOT_PATH / WORKSPACE_FILENAME, "w", encoding="utf-8") as file:
            file.write(json.dumps({"projects": {}, "plugins": ["foo.bar"]}))
        # WHEN I load the workspace from that directory
        with pytest.raises(WorkspacePluginError):
            Workspace.from_path(ROOT_PATH)
        # THEN the correct exception is raised
