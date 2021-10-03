import os
import shutil
import subprocess

import pytest

from tests.cli.commands.constants import PROJECT_ROOT
from workspaces.core.settings import get_settings


@pytest.fixture(autouse=True)
def setup_root_project():
    if not PROJECT_ROOT.exists():
        os.mkdir(PROJECT_ROOT)
    try:
        subprocess.run(["workspaces", "init", "--path", PROJECT_ROOT], check=True, capture_output=True)
        assert (PROJECT_ROOT / get_settings().project_filename).exists()
        yield
    finally:
        shutil.rmtree(PROJECT_ROOT)
