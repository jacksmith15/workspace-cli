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
@click.option(
    "--dev",
    "-d",
    type=bool,
    help="Include development dependencies.",
    default=False,
)
def sync(targets: Tuple[str, ...], dev: bool = False):
    """Runs command ARGS in each target workspace tracked by the current project."""
    project = WorkspacesProject.from_path()

    if targets:
        target_set = resolve_targets(project, set(targets))
    else:
        target_set = set(project.workspaces)

    if not target_set:
        click.echo(theme.attention("No workspaces selected."))
        sys.exit(0)

    exit_codes = {0}
    for target in sorted(target_set):
        exit_codes.add(project.workspaces[target].adapter.sync(include_dev=dev).returncode)

    exit_code = sorted(exit_codes, key=lambda code: abs(code), reverse=True)[0]
    if exit_code != 0:
        click.echo(theme.error("Some workspaces failed"))

    sys.exit(exit_code)
