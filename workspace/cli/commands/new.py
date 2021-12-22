import shutil
import sys
from pathlib import Path

import click

from workspace.cli import theme, utils
from workspace.cli.exceptions import WorkspaceCLIError
from workspace.core.adapter import get_adapter, get_adapters
from workspace.core.models import Workspace


@click.command()
@click.argument(
    "path",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option("--type", type=str, help="The type of project to create.")
@click.option(
    "--name", type=str, default=None, help="Name of the project. If not provided, the directory name will be used."
)
@click.option(
    "--template",
    type=str,
    default=None,
    help="Specify a template to use. Must be discoverable on the template path. Optional if `type` is specified, and the type adapter provides a default template.",
)
def new(path: Path, type: str = None, name: str = None, template: str = None):
    """Create a new project in the workspace.

    Either specify a template to use, or specify the type to use the default template.
    """
    workspace = Workspace.from_path()

    existing = workspace.get_project_by_path(path)
    if existing:
        theme.echo(f"<e>Path <b>{path}</b> already tracked as project <b>{existing.name}</b>.</e>")
        sys.exit(1)

    name = name or path.name
    if path.resolve().exists():
        theme.echo(
            f"""<e>Path <b>{path}</b> already exists.</e>

Run the following to track an existing project:

    <a>workspace <b>add</b> {path}</a>
"""
        )
        sys.exit(1)

    if name in workspace.projects:
        theme.echo(
            f"""<e>Project <b>{name}</b> already exists.</e>

Specify a different name with:

    <a>workspace new{f" --type {type}" if type else ""}{f" --template {template}" if template else ""} <b>--name NAME</b> {path}
"""
        )
        sys.exit(1)

    if template and template not in workspace.templates:
        template_list = "\n".join([f"  - <a>{path.name}</a>" for path in workspace.templates])
        raise WorkspaceCLIError(
            f"""<e>Unknown template <b>{template}</b>.</e>

Available templates are:
{template_list}

"""
        )

    try:
        _initialise_template(workspace, path=path.resolve(), type=type, name=name, template=template)
        type = type or utils.detect_type(workspace, path.resolve())
        if not type:
            valid_type_list = "\n".join([f"  - <b>{name}</b>" for name in get_adapters()])
            template_path = workspace.templates[template]  # type: ignore[index]
            raise WorkspaceCLIError(
                f"""
<e>Could not detect type of generated project.</e>

This is likely an issue with the template at <b>{template_path}</b>.

You can specify the intended type for more detailed information:

    <a>workspace add --template {template} --type <b>TYPE</b> {path}</a>

Available types are:
{valid_type_list}
"""
            )
        project = workspace.set_project(
            name=name,
            path=str(Path.cwd().relative_to(workspace.path) / path),
            type=type,
        )
        project.adapter.validate()
        workspace.flush()
    except Exception as exc:
        if path.exists():
            shutil.rmtree(path.resolve())
        raise exc
    else:
        theme.echo(f"Created new project <a>{name}</a> at <a>{path}</a>.")
        sys.exit(0)


def _initialise_template(workspace: Workspace, path: Path, name: str, type: str = None, template: str = None):
    """Initialise the project directory."""
    if template:
        workspace.templates.create(
            template, path=path, name=name
        )
    else:
        if not type:
            raise WorkspaceCLIError("<e>Must specify at least one of <b>--type</b> and <b>--template</b> options.</e>")
        adapter = get_adapter(type)
        try:
            adapter.new(path)
        except NotImplementedError:
            raise WorkspaceCLIError(
                f"""<e>Type <b>{type}</b> does not have a default template.</e>

Please provide one, e.g.

    <a>workspace new {path} --type {type} --template TEMPLATE</a>
"""
            )
