import sys
from pathlib import Path

import click

from workspace.cli import theme
from workspace.core.models import Workspace


@click.command()
@click.argument(
    "action",
    type=click.Choice(["add", "remove"]),
)
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
def path(action: str, path: Path):
    workspace = Workspace.from_path()

    path = path.resolve().relative_to(workspace.path)

    if not workspace.template_path:
        workspace.template_path = []

    # TODO: it might be good to print the templates added and removed.
    if action == "add":
        if str(path) in workspace.template_path:
            theme.echo(f"<e>Already configured to detect templates at <b>{path}</b>.</e>")
            sys.exit(1)
        workspace.template_path.append(str(path))
        workspace.flush()
        theme.echo(f"Added <a>{path}</a> to available template directories.")
        sys.exit(0)

    if str(path) not in workspace.template_path:
        theme.echo(f"<e>Not configured to detect templates at <b>{path}</b>.</e>")
        sys.exit(1)

    workspace.template_path.remove(str(path))
    workspace.flush()
    theme.echo(f"Stopped detecting templates at <a>{path}</a>.")
