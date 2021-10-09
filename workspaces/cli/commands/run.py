import sys
from typing import Tuple

import click

from workspaces.cli import callbacks, theme
from workspaces.cli.utils import resolve_targets
from workspaces.core.models import Workspace, WorkspacesProject


@click.command()
@click.argument(
    "targets",
    nargs=-1,
    callback=callbacks.consume_stdin,
)
@click.option(
    "--command",
    "-c",
    type=str,
    required=True,
    help="The command to execute in the target workspaces.",
)
def run(targets: Tuple[str], command: str):
    """Run a command in each target workspace."""
    project = WorkspacesProject.from_path()

    if targets:
        target_set = resolve_targets(project, set(targets))
    else:
        target_set = set(project.workspaces)

    if not target_set:
        theme.echo("<w>No workspaces selected.</w>")
        sys.exit(0)

    exit_codes = {0}
    for target in sorted(target_set):
        exit_codes.add(_run_in_workspace(project.workspaces[target], command))

    exit_code = sorted(exit_codes, key=lambda code: abs(code), reverse=True)[0]
    if exit_code != 0:
        theme.echo("<e>Some workspaces failed.</e>")

    sys.exit(exit_code)


def _run_in_workspace(workspace: Workspace, command: str) -> int:
    theme.echo(f"\n<h>Running <b>{command}</b> in <b>{workspace.path}</b>...</h>\n")
    result = workspace.adapter.run(command)
    return result.returncode
