import sys

import click

from workspaces.cli import theme
from workspaces.cli.commands.add import add
from workspaces.cli.commands.dependees import dependees
from workspaces.cli.commands.init import init
from workspaces.cli.commands.list import list_
from workspaces.cli.commands.remove import remove
from workspaces.cli.commands.reverse import reverse
from workspaces.cli.commands.run import run
from workspaces.core.exceptions import WorkspacesError


@click.group()
def cli():
    """Manage interdependent project workspaces."""
    pass


for command in (add, dependees, init, list_, remove, reverse, run):
    cli.add_command(command)


def run_cli():
    # load plugins?
    try:
        cli()
    except WorkspacesError as exc:
        click.echo(theme.error(str(exc)))
        sys.exit(1)
