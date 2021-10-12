import click

from workspace.cli import theme
from workspace.core.models import Workspace


@click.command("list")
def list_():
    workspace = Workspace.from_path()
    output = {
        template_path.name: str(template_path.relative_to(workspace.path)) for template_path in workspace.templates
    }
    if not output:
        return
    maxlen = max([len(name) for name in output])
    theme.echo("")
    for template_path in workspace.templates:
        theme.echo(
            f"<b>{template_path.name.ljust(maxlen)}</b>   <a>{template_path.relative_to(workspace.path)}</a>", err=False
        )
