import os
import shutil

import pytest

from tests.cli.commands.constants import WORKSPACE_ROOT
from tests.cli.commands.helpers import run
from workspace.core.settings import get_settings


@pytest.fixture(autouse=True)
def setup_root_project():
    if not WORKSPACE_ROOT.exists():
        os.mkdir(WORKSPACE_ROOT)
    existing = set(WORKSPACE_ROOT.glob("**/*"))
    try:
        run(["workspace", "init", "--path", WORKSPACE_ROOT])
        assert (WORKSPACE_ROOT / get_settings().filename).exists()
        yield
    finally:
        for path in WORKSPACE_ROOT.glob("**/*"):
            if path not in existing:
                if not path.exists():
                    continue
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()


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


@pytest.fixture(autouse=True)
def _set_python_path():
    """Set the pythonpath to project root.

    This allows subprocess CLI calls to detect plugins, if configured.
    """
    PYTHONPATH = "PYTHONPATH"
    original = os.environ.get(PYTHONPATH, None)
    try:
        os.environ[PYTHONPATH] = str(WORKSPACE_ROOT)
        yield
    finally:
        if original:
            os.environ[PYTHONPATH] = original
        else:
            if PYTHONPATH in os.environ:
                del os.environ[PYTHONPATH]
