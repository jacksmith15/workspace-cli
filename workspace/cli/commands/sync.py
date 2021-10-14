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
@click.option(
    "--dev/--no-dev",
    "-D/ ",
    type=bool,
    help="Include development dependencies.",
    default=False,
)
def sync(specifiers: Tuple[str, ...], dev: bool = False):
    """Sync the environments of the specified projects."""
    workspace = Workspace.from_path()

    if specifiers:
        target_set = resolve_specifiers(workspace, set(specifiers))
    else:
        target_set = set(workspace.projects)

    if not target_set:
        theme.echo("<w>No projects selected.</w>")
        sys.exit(0)

    exit_codes = {0}
    for target in sorted(target_set):
        theme.echo(f"Syncing environment for <b>{target}</b>\n")
        adapter = workspace.projects[target].adapter
        command = adapter.sync_command(include_dev=dev)
        exit_codes.add(adapter.run(command).returncode)

    exit_code = sorted(exit_codes, key=lambda code: abs(code), reverse=True)[0]
    if exit_code != 0:
        theme.echo("<e>Some projects failed.</e>")

    sys.exit(exit_code)
