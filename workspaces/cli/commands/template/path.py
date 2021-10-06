import sys
from pathlib import Path

import click

from workspaces.cli import theme
from workspaces.core.models import WorkspacesProject


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
    project = WorkspacesProject.from_path()

    path = path.resolve().relative_to(project.path)

    if not project.template_path:
        project.template_path = []

    # TODO: it might be good to print the templates added and removed.
    if action == "add":
        if str(path) in project.template_path:
            theme.echo(f"<e>Already configured to detect templates at <b>{path}</b>.</e>")
            sys.exit(1)
        project.template_path.append(str(path))
        project.flush()
        theme.echo(f"Added <a>{path}</a> to available template directories.")
        sys.exit(0)

    if str(path) not in project.template_path:
        theme.echo(f"<e>Not configured to detect templates at <b>{path}</b>.</e>")
        sys.exit(1)

    project.template_path.remove(str(path))
    project.flush()
    theme.echo(f"Stopped detecting templates at <a>{path}</a>.")
