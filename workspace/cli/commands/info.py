import json
from textwrap import indent

import click

from workspace.cli import theme
from workspace.core.models import Workspace


@click.command()
@click.option(
    "--output",
    "-o",
    type=click.Choice(("default", "json")),
    help="Select the output format. By default, just the workspace names will be shown.",
    default="default",
)
def info(output: str = "default"):
    """Display information about the current workspace and its projects."""
    workspace = Workspace.from_path()
    if output == "json":
        theme.echo(
            json.dumps(
                {
                    "path": str(workspace.path),
                    "projects": {
                        name: {"path": str(project.path), "type": project.type}
                        for name, project in workspace.projects.items()
                    },
                    "plugins": workspace.plugins,
                    "template_path": workspace.template_path,
                }
            ),
            err=False,
        )
    else:
        projects_table = theme.table(
            [(name, project.path, f"({project.type})") for name, project in workspace.projects.items()],
            ("bold", "accent", None),
        )
        plugin_list = theme.table([(plugin,) for plugin in workspace.plugins or []], ("bold",))
        template_path = "[" + ", ".join([f"<a>{path}</a>" for path in workspace.template_path or []]) + "]"
        theme.echo(
            f"""
<h>Path</h>: <a>{workspace.path}</a>
<h>Projects</h>:
{indent(projects_table, " " * 4)}
<h>Plugins</h>:
{indent(plugin_list, " " * 4)}
<h>Template Path</h>: {template_path}
""",
            err=False,
        )
