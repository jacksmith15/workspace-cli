import shutil
import sys

import click

from workspaces.cli import theme
from workspaces.core.models import WorkspacesProject


@click.command()
@click.argument(
    "name",
    type=str,
)
@click.option("--delete", "-d", type=bool, default=False, help="Delete the workspace content too.")
def remove(name: str, delete: bool = False):
    """Remove workspace NAME from project."""
    project = WorkspacesProject.from_path()

    if name not in project.workspaces:
        click.echo(theme.error(f"Unknown workspace {theme.error(name, accent=True)}."), err=True)
        sys.exit(1)

    resolved_path = project.workspaces[name].resolved_path
    del project.workspaces[name]
    project.flush()
    if delete:
        print("NOOOOO")
        # shutil.rmtree(resolved_path)
