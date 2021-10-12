import sys
from pathlib import Path

import click

from workspace.cli import theme
from workspace.core.models import Workspace
from workspace.core.settings import get_settings


@click.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
)
def init(path: Path = None):
    """Initialise a workspace."""
    path = (path or Path.cwd()).resolve() / get_settings().filename
    if path.exists():
        theme.echo(f"<e>File already exists at <b>{path}</b></e>.")
        sys.exit(1)
    workspace = Workspace(path.parent, projects={})
    workspace.flush()
    theme.echo(f"Created workspace at <a>{path}</a>.")
