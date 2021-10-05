import sys
from pathlib import Path

import click

from workspaces.cli import theme, utils
from workspaces.core.adapter import get_adapters
from workspaces.core.models import WorkspacesProject


@click.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option("--type", type=str, help="The type of project to add.")
@click.option(
    "--name", type=str, default=None, help="Name of the project. If not provided, the directory name will be used."
)
def add(path: Path, type: str = None, name: str = None):
    """Begin tracking an existing project at PATH as a workspace."""
    project = WorkspacesProject.from_path()

    name = name or path.name
    if name in project.workspaces:
        theme.echo(
            f"""<e>Workspace <b>{name}</b> already exists.</e>

Specify a different name with:

    <a>workspaces add{f" --type {type}" if type else ""} <b>--name NAME</b> {path}
"""
        )
        sys.exit(1)

    existing = project.get_workspace_by_path(path)
    if existing:
        theme.echo(f"<e>Path <b>{path}</b> already tracked as workspace <b>{existing.name}</b>.</e>")
        sys.exit(1)

    type = type or utils.detect_type(project, path)
    if not type:
        valid_type_list = "\n".join([f"  - <b>{name}</b>" for name in get_adapters()])
        theme.echo(
            f"""<e>Could not detect type of project at path <b>{path}</b>.</e>

Please specify type as follows:

    <a>workspaces add --type <b>TYPE</b> {path}</a>

Available types are:
{valid_type_list}
"""
        )
        sys.exit(1)

    workspace = project.set_workspace(
        name=name,
        path=str(Path.cwd().relative_to(project.path) / path),
        type=type,
    )
    workspace.adapter.validate()
    project.flush()
    theme.echo(f"Added new workspace <a>{workspace.name}</a> at <a>{path}</a>.")
