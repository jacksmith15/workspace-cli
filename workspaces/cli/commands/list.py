import json
import sys
from typing import Tuple

import click

from workspaces.cli import callbacks, theme
from workspaces.cli.utils import resolve_targets
from workspaces.core.models import WorkspacesProject


@click.command("list")
@click.argument(
    "targets",
    nargs=-1,
    callback=callbacks.consume_stdin,
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(("default", "names", "json")),
    help="Select the output format. By default, just the workspace names will be shown.",
    default="default",
)
def list_(targets: Tuple[str, ...], output: str = "default"):
    """Lists workspaces tracked in current project."""
    project = WorkspacesProject.from_path()

    if targets:
        target_set = resolve_targets(project, targets)
    else:
        target_set = set(project.workspaces)

    if not target_set:
        sys.exit(0)

    for name in sorted(target_set):
        workspace = project.workspaces[name]
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
