import shutil
import sys
from typing import Tuple

import click

from workspace.cli import callbacks, theme
from workspace.cli.utils import resolve_specifiers
from workspace.core.models import Workspace


@click.command()
@click.argument(
    "specifiers",
    nargs=-1,
    callback=callbacks.consume_stdin,
)
@click.option("--delete/--no-delete", "-d/ ", type=bool, default=False, help="Delete the workspace content too.")
def remove(specifiers: Tuple[str, ...], delete: bool = False):
    """Remove project(s) from the workspace.

    By default the project files will not be deleted, just untracked. Add the --delete flag to remove the directory.
    """
    workspace = Workspace.from_path()

    target_set = resolve_specifiers(workspace, specifiers)

    if not target_set:
        theme.echo("<w>No projects selected.</w>")
        sys.exit(0)

    for name in target_set:
        resolved_path = workspace.projects[name].resolved_path
        del workspace.projects[name]
        workspace.flush()
        if delete:
            shutil.rmtree(resolved_path)

    names = "\n".join(f"  - <b>{name}</b>" for name in target_set)
    if delete:
        theme.echo(
            f"""<w>Deleted projects:</w>
{names}
"""
        )
    else:
        theme.echo(
            f"""Stopped tracking projects:
{names}
"""
        )
