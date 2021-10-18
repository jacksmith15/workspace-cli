import sys
from collections import defaultdict
from functools import lru_cache
from typing import DefaultDict, Dict, Set, Tuple

import click

from workspace.cli import callbacks, theme
from workspace.cli.utils import resolve_specifiers
from workspace.core.models import Workspace


@click.command()
@click.argument(
    "specifiers",
    nargs=-1,
    callback=callbacks.consume_stdin,
)
@click.option("--transitive/--no-transitive", type=bool, default=True, help="Only show direct dependencies.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(("lines", "csv")),
    help="Select the output format.",
    default="lines",
)
@click.option(
    "--dev/--no-dev",
    "-d/ ",
    type=bool,
    help="Include development dependencies.",
    default=False,
)
def dependencies(specifiers: Tuple[str, ...], transitive: bool = True, output: str = "lines", dev: bool = False):
    """Get the set of all projects which are dependencies of the specified projects."""
    workspace = Workspace.from_path()

    target_set = resolve_specifiers(workspace, specifiers)

    if not target_set:
        theme.echo("<w>No projects selected.</w>")
        sys.exit(0)

    # Get a full map of dependencies:
    dependency_map = _get_dependency_map(workspace, transitive=transitive, include_dev=dev)

    # Extract the relevant dependencies:
    dependencies_set = {dependency for target in target_set for dependency in dependency_map[target]}

    # Sort them from least dependencies, to most dependencies:
    sorted_dependencies = [
        name
        for name, _ in sorted(dependency_map.items(), key=lambda item: len(item[1]))
        if name in dependencies_set or name in target_set
    ]

    if output == "csv":
        theme.echo(",".join(sorted_dependencies), err=False)
        sys.exit(0)

    for dependency in sorted_dependencies:
        theme.echo(dependency, err=False)
    sys.exit(0)


def _get_dependency_map(
    workspace: Workspace,
    transitive: bool = True,
    include_dev: bool = False,
) -> Dict[str, Set[str]]:
    """Get a mapping of projects to their dependencies."""

    direct_map: DefaultDict[str, Set[str]] = defaultdict(set)
    for name, project in workspace.projects.items():
        direct_map[name] |= project.adapter.dependencies(include_dev=include_dev)
    if not transitive:
        return dict(direct_map)

    @lru_cache(maxsize=None)
    def get_dependencies(name: str):
        dependencies = set(direct_map[name])
        for dependency in set(dependencies):
            dependencies |= get_dependencies(dependency)
        return dependencies

    return {name: get_dependencies(name) for name in workspace.projects}
