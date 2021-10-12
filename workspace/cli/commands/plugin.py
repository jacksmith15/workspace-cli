import importlib

import click

from workspace.cli import theme
from workspace.cli.exceptions import WorkspaceCLIError
from workspace.core.adapter import Adapter
from workspace.core.models import Workspace


@click.group()
def plugin():
    """Commands for managing workspace plugins."""
    pass


@plugin.command()
@click.argument("module_path", type=str)
def add(module_path: str):
    """Add a plugin by its Python module path."""
    workspace = Workspace.from_path()

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise WorkspaceCLIError(
            f"""<e>Could not import plugin <b>{module_path}</b>.</e>

The plugin must be available on your <a>PYTHONPATH</a>.
"""
        )
    workspace.plugins = workspace.plugins or []
    if module_path in workspace.plugins:
        raise WorkspaceCLIError(f"<e>Plugin <b>{module_path}</b> already installed.</e>")
    workspace.plugins.append(module_path)
    workspace.flush()
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
<h>The following new project types are now available:</h>
{new_types}
"""
        )


@plugin.command()
@click.argument("module_path", type=str)
def remove(module_path: str):
    """Remove a plugin by its Python module path."""
    workspace = Workspace.from_path()

    workspace.plugins = workspace.plugins or []
    if module_path not in workspace.plugins:
        raise WorkspaceCLIError(f"<e>Plugin <b>{module_path}</b> not installed.</e>")
    workspace.plugins.remove(module_path)
    workspace.flush()
    theme.echo(f"Removed plugin <s>{module_path}</s>.")


@plugin.command("list")
def list_():
    workspace = Workspace.from_path()
    for plugin in workspace.plugins or []:
        theme.echo(plugin)
