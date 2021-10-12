import json
import sys
from typing import Tuple

import click

from workspace.cli import callbacks, theme
from workspace.cli.utils import resolve_specifiers
from workspace.core.models import Workspace


@click.command("list")
@click.argument(
    "specifiers",
    nargs=-1,
    callback=callbacks.consume_stdin,
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(("default", "names", "json")),
    help="Select the output format. By default, just the project names will be shown.",
    default="default",
)
def list_(specifiers: Tuple[str, ...], output: str = "default"):
    """List projects tracked in the workspace."""
    workspace = Workspace.from_path()

    if specifiers:
        target_set = resolve_specifiers(workspace, specifiers)
    else:
        target_set = set(workspace.projects)

    if not target_set:
        sys.exit(0)

    for name in sorted(target_set):
        project = workspace.projects[name]
        if output == "json":
            theme.echo(
                json.dumps(
                    {
                        "name": project.name,
                        "type": project.type,
                        "path": str(workspace.path / project.path),
                        "depends_on": list(project.adapter.dependencies()),
                    }
                ),
                err=False,
            )
        elif output == "names":
            theme.echo(project.name, err=False)
        else:
            theme.echo(
                f"""
<h>Name</h>: <b>{project.name}</b>
<h>Type</h>: {project.type}
<h>Path</h>: <a>{workspace.path / project.path}</a>
<h>Dependencies</h>: [{", ".join(project.adapter.dependencies())}]""",
                err=False,
            )
