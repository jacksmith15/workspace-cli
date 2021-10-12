import sys
from pathlib import Path

import click

from workspace.cli import theme, utils
from workspace.core.adapter import get_adapters
from workspace.core.models import Workspace


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
    """Track an existing project at PATH in the workspace."""
    workspace = Workspace.from_path()

    name = name or path.name
    if name in workspace.projects:
        theme.echo(
            f"""<e>Project <b>{name}</b> already exists.</e>

Specify a different name with:

    <a>workspace add{f" --type {type}" if type else ""} <b>--name NAME</b> {path}
"""
        )
        sys.exit(1)

    existing = workspace.get_project_by_path(path)
    if existing:
        theme.echo(f"<e>Path <b>{path}</b> already tracked as project <b>{existing.name}</b>.</e>")
        sys.exit(1)

    type = type or utils.detect_type(workspace, path)
    if not type:
        valid_type_list = "\n".join([f"  - <b>{name}</b>" for name in get_adapters()])
        theme.echo(
            f"""<e>Could not detect type of project at path <b>{path}</b>.</e>

Please specify type as follows:

    <a>workspace add --type <b>TYPE</b> {path}</a>

Available types are:
{valid_type_list}
"""
        )
        sys.exit(1)

    project = workspace.set_project(
        name=name,
        path=str(Path.cwd().relative_to(workspace.path) / path),
        type=type,
    )
    project.adapter.validate()
    workspace.flush()
    theme.echo(f"Added new project <a>{project.name}</a> at <a>{path}</a>.")
