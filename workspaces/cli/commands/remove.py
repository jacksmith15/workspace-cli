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
@click.option("--delete/--no-delete", "-d/ ", type=bool, default=False, help="Delete the workspace content too.")
def remove(name: str, delete: bool = False):
    """Remove workspace NAME from project."""
    project = WorkspacesProject.from_path()

    if name not in project.workspaces:
        workspaces = "\n".join((f"  - <a>{name}</a>" for name in list(project.workspaces)[:10]))
        theme.echo(
            f"""<e>Unknown workspace <b>{name}</b>.</e>

Did you mean one of these?
{workspaces}
"""
        )
        sys.exit(1)

    resolved_path = project.workspaces[name].resolved_path
    del project.workspaces[name]
    project.flush()
    if delete:
        shutil.rmtree(resolved_path)
        theme.echo(f"<w>Deleted workspace <b>{name}</b></w>.")
    else:
        theme.echo(f"Stopped tracking workspace <a>{name}</a>.")
