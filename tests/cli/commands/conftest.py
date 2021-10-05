import os
import shutil

import pytest

from tests.cli.commands.constants import PROJECT_ROOT
from tests.cli.commands.helpers import run
from workspaces.core.settings import get_settings


@pytest.fixture(autouse=True)
def setup_root_project():
    if not PROJECT_ROOT.exists():
        os.mkdir(PROJECT_ROOT)
    try:
        run(["workspaces", "init", "--path", PROJECT_ROOT])
        assert (PROJECT_ROOT / get_settings().project_filename).exists()
        yield
    finally:
        shutil.rmtree(PROJECT_ROOT)


@pytest.fixture(autouse=True)
def _unset_virtual_env():
    """Poetry automatically uses activated virtualenvs.

    By unsetting the VIRTUAL_ENV environment variable, we trick poetry into creating new
    ones instead. This prevents the root project venv being polluted on test runs.
    """
    if "VIRTUAL_ENV" in os.environ:
        original = os.environ["VIRTUAL_ENV"]
        try:
            del os.environ["VIRTUAL_ENV"]
            yield
        finally:
            os.environ["VIRTUAL_ENV"] = original
    else:
        yield
