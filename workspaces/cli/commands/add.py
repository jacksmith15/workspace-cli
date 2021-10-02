import sys
from pathlib import Path

import click

from workspaces.cli import theme
from workspaces.core.models import WorkspacesProject


@click.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option("--type", "-t", type=str, required=True, help="The type of project to add.")
@click.option(
    "--name", type=str, default=None, help="Name of the project. If not provided, the directory name will be used."
)
def add(path: Path, type: str, name: str = None):
    """Begin tracking an existing Python project at PATH as a workspace."""
    project = WorkspacesProject.from_path()
    path = Path.cwd().relative_to(project.path) / path

    name = name or path.name
    if name in project.workspaces:
        click.echo(theme.error(f"Workspace {name!r} already exists."), err=True)
        sys.exit(1)

    existing = project.get_workspace_by_path(path)
    if existing:
        click.echo(theme.error(f"Path {str(path)!r} already tracked as workspace {existing!r}."))
        sys.exit(1)

    workspace = project.set_workspace(
        name=name,
        path=str(path),
        type=type,
    )
    workspace.adapter.validate()
    project.flush()
    click.echo(theme.header(f"Added new workspace {workspace.name!r}."))
