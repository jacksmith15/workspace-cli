import sys
from pathlib import Path

import click

from workspaces.cli import theme
from workspaces.core.models import WorkspacesProject
from workspaces.core.settings import get_settings


@click.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
)
def init(path: Path = None):
    """Initialise a workspaces root project."""
    path = (path or Path.cwd()).resolve() / get_settings().project_filename
    if path.exists():
        theme.echo(f"<e>File already exists at <b>{path}</b></e>.")
        sys.exit(1)
    project = WorkspacesProject(path.parent, workspaces={})
    project.flush()
    theme.echo(f"Created workspaces project at <a>{path}</a>.")
