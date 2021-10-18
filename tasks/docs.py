import os
import subprocess
from pathlib import Path

from invoke import Collection, task


@task
def build(ctx):
    """Build the docs."""
    subprocess.run(["mkdocs", "build", "-d", "build/"], **_run_kwargs())


@task
def serve(ctx, port=8080):
    """Serve the docs locally."""
    subprocess.run(["mkdocs", "serve", "-a", f"localhost:{port}"], **_run_kwargs())


def _run_kwargs():
    return dict(cwd=Path(__file__).parent.parent / "docs", env={**os.environ.copy(), "PYTHONPATH": "."})


docs = Collection("docs", build, serve)
