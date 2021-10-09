import json
from textwrap import indent

import click

from workspaces.cli import theme
from workspaces.core.models import WorkspacesProject


@click.command()
@click.option(
    "--output",
    "-o",
    type=click.Choice(("default", "json")),
    help="Select the output format. By default, just the workspace names will be shown.",
    default="default",
)
def info(output: str = "default"):
    """Display information about the current project and its workspaces."""
    project = WorkspacesProject.from_path()
    if output == "json":
        theme.echo(
            json.dumps(
                {
                    "path": str(project.path),
                    "workspaces": {
                        name: {"path": str(workspace.path), "type": workspace.type}
                        for name, workspace in project.workspaces.items()
                    },
                    "plugins": project.plugins,
                    "template_path": project.template_path,
                }
            ),
            err=False,
        )
    else:
        workspace_table = theme.table(
            [(name, workspace.path, f"({workspace.type})") for name, workspace in project.workspaces.items()],
            ("bold", "accent", None),
        )
        plugin_list = theme.table([(plugin,) for plugin in project.plugins or []], ("bold",))
        template_path = "[" + ", ".join([f"<a>{path}</a>" for path in project.template_path or []]) + "]"
        theme.echo(
            f"""
<h>Path</h>: <a>{project.path}</a>
<h>Workspaces</h>:
{indent(workspace_table, " " * 4)}
<h>Plugins</h>:
{indent(plugin_list, " " * 4)}
<h>Template Path</h>: {template_path}
""",
            err=False,
        )
