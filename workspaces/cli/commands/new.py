import shutil
import sys
from pathlib import Path

import click

from workspaces.cli import theme, utils
from workspaces.cli.exceptions import WorkspacesCLIError
from workspaces.core.adapter import get_adapter, get_adapters
from workspaces.core.models import WorkspacesProject


@click.command()
@click.argument(
    "path",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option("--type", type=str, help="The type of project to add.")
@click.option(
    "--name", type=str, default=None, help="Name of the project. If not provided, the directory name will be used."
)
@click.option(
    "--template",
    type=str,
    default=None,
    help="Specify a template to use. Must be discoverable on the template path. Optional if `type` is specified, and the type provides a default template.",
)
def new(path: Path, type: str = None, name: str = None, template: str = None):
    project = WorkspacesProject.from_path()

    existing = project.get_workspace_by_path(path)
    if existing:
        theme.echo(f"<e>Path <b>{path}</b> already tracked as workspace <b>{existing.name}</b>.</e>")
        sys.exit(1)

    name = name or path.name
    if path.resolve().exists():
        theme.echo(
            f"""<e>Path <b>{path}</b> already exists.</e>

Run the following to track an existing project:

    <a>workspaces <b>add</b> {path}</a>
"""
        )
        sys.exit(1)

    if name in project.workspaces:
        theme.echo(
            f"""<e>Workspace <b>{name}</b> already exists.</e>

Specify a different name with:

    <a>workspaces new{f" --type {type}" if type else ""}{f" --template {template}" if template else ""} <b>--name NAME</b> {path}
"""
        )
        sys.exit(1)

    try:
        _initialise_template(project, path=path.resolve(), type=type, template=template)
        type = type or utils.detect_type(project, path.resolve())
        if not type:
            valid_type_list = "\n".join([f"  - <b>{name}</b>" for name in get_adapters()])
            raise WorkspacesCLIError(
                f"""
<e>Could not detect type of generated project.</e>

This is likely an issue with the template at <b>{project.templates[template]}</b>.

You can specify the intended type for more detailed information:

    <a>workspaces add --type <b>TYPE</b> {path}</a>

Available types are:
{valid_type_list}
"""
            )
        workspace = project.set_workspace(
            name=name,
            path=str(Path.cwd().relative_to(project.path) / path),
            type=type,
        )
        workspace.adapter.validate()
        project.flush()
    except Exception as exc:
        if path.exists():
            shutil.rmtree(path.resolve())
        raise exc
    else:
        theme.echo(f"Created new workspace <a>{name}</a> at <a>{path}</a>.")
        sys.exit(0)


def _initialise_template(project: WorkspacesProject, path: Path, type: str = None, template: str = None):
    """Initialise the workspace directory."""
    if template:
        project.templates.create(template, path)
    else:
        if not type:
            raise WorkspacesCLIError("<e>Must specify at least one of <b>--type</b> and <b>--template</b> options.</e>")
        adapter = get_adapter(type)
        try:
            adapter.new(path)
        except NotImplementedError:
            raise WorkspacesCLIError(
                f"""<e>Type <b>{type}</b> does not have a default template.</e>

Please provide one, e.g.

    <a>workspaces new {path} --type {type} --template TEMPLATE</a>
"""
            )
