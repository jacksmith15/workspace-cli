import click

from workspaces.cli import theme
from workspaces.core.models import WorkspacesProject


@click.command("list")
def list_():
    project = WorkspacesProject.from_path()
    output = {template_path.name: str(template_path.relative_to(project.path)) for template_path in project.templates}
    if not output:
        return
    maxlen = max([len(name) for name in output])
    theme.echo("")
    for template_path in project.templates:
        theme.echo(
            f"<b>{template_path.name.ljust(maxlen)}</b>   <a>{template_path.relative_to(project.path)}</a>", err=False
        )
