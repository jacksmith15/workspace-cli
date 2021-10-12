import click

from workspace.cli.commands.template.list import list_
from workspace.cli.commands.template.path import path


@click.group()
def template():
    """Commands for managing project templates."""
    pass


template.add_command(list_)
template.add_command(path)
