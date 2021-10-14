import sys
from typing import Tuple

import click

from workspace.cli import callbacks, runner, theme
from workspace.cli.utils import resolve_specifiers
from workspace.core.models import Workspace


@click.command()
@click.argument(
    "specifiers",
    nargs=-1,
    callback=callbacks.consume_stdin,
)
@click.option(
    "--command",
    "-c",
    type=str,
    required=True,
    help="The command to execute.",
)
@click.option(
    "--parallel/--no-parallel",
    "-p/ ",
    type=bool,
    default=False,
    help="Run the command in parallel.",
)
def run(specifiers: Tuple[str], command: str, parallel: bool = False):
    """Run a command in each project.

    If no specifiers are provided, the command will be run in all projects.
    """
    workspace = Workspace.from_path()

    if specifiers:
        target_set = resolve_specifiers(workspace, set(specifiers))
    else:
        target_set = set(workspace.projects)

    if not target_set:
        theme.echo("<w>No projects selected.</w>")
        sys.exit(0)

    project_commands = [(workspace.projects[target], command) for target in target_set]
    sys.exit(runner.run(project_commands, parallel=parallel))
