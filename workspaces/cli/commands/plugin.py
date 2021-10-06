import importlib

import click

from workspaces.cli import theme
from workspaces.cli.exceptions import WorkspacesCLIError
from workspaces.core.adapter import Adapter
from workspaces.core.models import WorkspacesProject


@click.group()
def plugin():
    """Commands for managing project plugins."""
    pass


@plugin.command()
@click.argument("module_path", type=str)
def add(module_path: str):
    """Add a plugin by its Python module path."""
    project = WorkspacesProject.from_path()

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise WorkspacesCLIError(
            f"""<e>Could not import plugin <b>{module_path}</b>.</e>

The plugin must be available on your <a>PYTHONPATH</a>.
"""
        )
    project.plugins = project.plugins or []
    if module_path in project.plugins:
        raise WorkspacesCLIError(f"<e>Plugin <b>{module_path}</b> already installed.</e>")
    project.plugins.append(module_path)
    project.flush()
    theme.echo(f"Added plugin <s>{module_path}</s>.")

    new_types = "\n".join(
        [
            f"  - <a>{cls.name}</a>"
            for cls in vars(module).values()
            if isinstance(cls, type) and issubclass(cls, Adapter) and not cls is Adapter
        ]
    )
    if new_types:
        theme.echo(
            f"""
<h>The following new workspace types are now available:</h>
{new_types}
"""
        )


@plugin.command()
@click.argument("module_path", type=str)
def remove(module_path: str):
    """Remove a plugin by its Python module path."""
    project = WorkspacesProject.from_path()

    project.plugins = project.plugins or []
    if module_path not in project.plugins:
        raise WorkspacesCLIError(f"<e>Plugin <b>{module_path}</b> not installed.</e>")
    project.plugins.remove(module_path)
    project.flush()
    theme.echo(f"Removed plugin <s>{module_path}</s>.")


@plugin.command("list")
def list_():
    project = WorkspacesProject.from_path()
    for plugin in project.plugins:
        theme.echo(plugin)
