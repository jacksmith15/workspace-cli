import click

from workspaces.cli import theme
from workspaces.core.models import WorkspacesProject


@click.command("list")
def list_():
    """Lists workspaces tracked in current project."""
    project = WorkspacesProject.from_path()
    for workspace in project.workspaces:
        click.echo(theme.text(workspace))
