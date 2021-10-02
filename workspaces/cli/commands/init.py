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
    """Begin tracking an existing Python project at PATH as a workspace."""
    path = (path or Path.cwd()).resolve() / get_settings().project_filename
    if path.exists():
        click.echo(theme.error(f"File already exists at '{path}'."))
        sys.exit(1)
    click.echo(theme.header(f"Creating workspaces project at '{path}'..."))
    project = WorkspacesProject(path.parent, workspaces={})
    project.flush()
