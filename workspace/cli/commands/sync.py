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
    "--dev/--no-dev",
    "-D/ ",
    type=bool,
    help="Include development dependencies.",
    default=False,
)
@click.option(
    "--parallel/--no-parallel",
    "-p/ ",
    type=bool,
    default=False,
    help="Run the command in parallel.",
)
def sync(specifiers: Tuple[str, ...], dev: bool = False, parallel: bool = False):
    """Sync the environments of the specified projects."""
    workspace = Workspace.from_path()

    target_set = set(workspace.projects) if click.get_text_stream("stdin").isatty() else set()
    if specifiers:
        target_set = resolve_specifiers(workspace, specifiers)

    if not target_set:
        theme.echo("<w>No projects selected.</w>")
        sys.exit(0)

    projects = (workspace.projects[target] for target in target_set)
    project_commands = [(project, project.adapter.sync_command(include_dev=dev)) for project in projects]

    sys.exit(runner.run(project_commands, parallel=parallel))
