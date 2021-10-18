import sys

import click

from workspace.cli import theme
from workspace.cli.commands.add import add
from workspace.cli.commands.dependees import dependees
from workspace.cli.commands.dependencies import dependencies
from workspace.cli.commands.info import info
from workspace.cli.commands.init import init
from workspace.cli.commands.list import list_
from workspace.cli.commands.new import new
from workspace.cli.commands.plugin import plugin
from workspace.cli.commands.remove import remove
from workspace.cli.commands.reverse import reverse
from workspace.cli.commands.run import run
from workspace.cli.commands.sync import sync
from workspace.cli.commands.template import template
from workspace.cli.exceptions import WorkspaceCLIError
from workspace.core.exceptions import WorkspaceBaseError


@click.group()
def cli():
    """Manage interdependent projects in a workspace."""
    pass


for command in (add, dependees, dependencies, info, init, list_, new, plugin, remove, reverse, run, sync, template):
    cli.add_command(command)


def run_cli():
    try:
        cli()
    except WorkspaceCLIError as exc:
        theme.echo(exc.display)
        sys.exit(exc.exit_code)
    except WorkspaceBaseError as exc:
        theme.echo(f"<e>{exc}</e>")
        sys.exit(1)
