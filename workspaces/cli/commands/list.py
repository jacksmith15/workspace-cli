import json

import click

from workspaces.cli import theme
from workspaces.core.models import WorkspacesProject


@click.command("list")
@click.option(
    "--output",
    "-o",
    type=click.Choice(("default", "names", "json")),
    help="Select the output format. By default, just the workspace names will be shown.",
    default="default",
)
def list_(output: str = "default"):
    """Lists workspaces tracked in current project."""
    project = WorkspacesProject.from_path()
    for workspace in project.workspaces.values():
        if output == "json":
            theme.echo(
                json.dumps(
                    {
                        "name": workspace.name,
                        "type": workspace.type,
                        "path": str(project.path / workspace.path),
                        "depends_on": list(workspace.adapter.dependencies()),
                    }
                ),
                err=False,
            )
        elif output == "names":
            theme.echo(workspace.name, err=False)
        else:
            theme.echo(
                f"""
<h>Name</h>: <b>{workspace.name}</b>
<h>Type</h>: {workspace.type}
<h>Path</h>: <a>{project.path / workspace.path}</a>
<h>Dependencies</h>: [{", ".join(workspace.adapter.dependencies())}]""",
                err=False,
            )
