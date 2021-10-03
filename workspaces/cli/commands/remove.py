import shutil
import sys
from typing import Tuple

import click

from workspaces.cli import theme
from workspaces.cli.utils import resolve_targets
from workspaces.core.models import WorkspacesProject


@click.command()
@click.argument(
    "targets",
    nargs=-1,
)
@click.option("--delete/--no-delete", "-d/ ", type=bool, default=False, help="Delete the workspace content too.")
def remove(targets: Tuple[str, ...], delete: bool = False):
    """Remove workspace(s) from the project.

    By default they will not be deleted.
    """
    project = WorkspacesProject.from_path()

    target_set = resolve_targets(project, targets)

    if not target_set:
        theme.echo("<w>No workspaces selected.</w>")
        sys.exit(0)

    for name in target_set:
        resolved_path = project.workspaces[name].resolved_path
        del project.workspaces[name]
        project.flush()
        if delete:
            shutil.rmtree(resolved_path)

    names = "\n".join(f"  - <b>{name}</b>" for name in target_set)
    if delete:
        theme.echo(
            f"""<w>Deleted workspaces:</w>
{names}
"""
        )
    else:
        theme.echo(
            f"""Stopped tracking workspaces:
{names}
"""
        )
