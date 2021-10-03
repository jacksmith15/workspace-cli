import sys

import click

from workspaces.cli import theme
from workspaces.cli.commands.add import add
from workspaces.cli.commands.dependees import dependees
from workspaces.cli.commands.init import init
from workspaces.cli.commands.list import list_
from workspaces.cli.commands.new import new
from workspaces.cli.commands.remove import remove
from workspaces.cli.commands.reverse import reverse
from workspaces.cli.commands.run import run
from workspaces.cli.exceptions import WorkspacesCLIError
from workspaces.core.exceptions import WorkspacesError


@click.group()
def cli():
    """Manage interdependent project workspaces."""
    pass


for command in (add, dependees, init, list_, new, remove, reverse, run):
    cli.add_command(command)


def run_cli():
    try:
        cli()
    except WorkspacesCLIError as exc:
        theme.echo(exc.display)
        sys.exit(exc.exit_code)
    except WorkspacesError as exc:
        theme.echo(f"<e>{exc}</e>")
        sys.exit(1)
