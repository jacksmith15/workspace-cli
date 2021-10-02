import sys
from typing import Tuple

import click

from workspaces.cli import theme
from workspaces.cli.utils import resolve_targets
from workspaces.core.models import Workspace, WorkspacesProject


@click.command()
@click.argument(
    "args",
    nargs=-1,
)
@click.option(
    "--targets",
    "-t",
    type=str,
    default=None,
    help="Comma-separated list of target workspaces by name. Omit to run the command in all tracked workspaces.",
)
def run(args: Tuple[str, ...], targets: str = None):
    """Runs command ARGS in each target workspace tracked by the current project."""
    project = WorkspacesProject.from_path()

    if targets:
        target_set = resolve_targets(project, set(targets.split(",")))
    else:
        target_set = set(project.workspaces)

    if not target_set:
        click.echo(theme.attention("No workspaces selected."))
        sys.exit(0)

    exit_codes = {0}
    for target in sorted(target_set):
        exit_codes.add(_run_in_workspace(project.workspaces[target], args))

    exit_code = sorted(exit_codes, key=lambda code: abs(code), reverse=True)[0]
    if exit_code != 0:
        click.echo(theme.error("Some workspaces failed"))

    sys.exit(exit_code)


def _run_in_workspace(workspace: Workspace, args: Tuple[str, ...]):
    click.echo(theme.header(f"\nRunning '{' '.join(args)}' in '{workspace.resolved_path}'...\n"))
    result = workspace.adapter.run(list(args))
    return result.returncode
