import sys
from collections import defaultdict
from functools import lru_cache
from typing import Dict, Set, Tuple

import click

from workspaces.cli import callbacks, theme
from workspaces.cli.utils import resolve_targets
from workspaces.core.models import WorkspacesProject


@click.command()
@click.argument(
    "targets",
    nargs=-1,
    callback=callbacks.consume_stdin,
)
@click.option("--transitive/--no-transitive", type=bool, default=True, help="Only show direct dependees.")
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
def dependees(targets: Tuple[str, ...], transitive: bool = True, output: str = "lines", dev: bool = False):
    """Get the set of workspaces which depend on the specified workspaces."""
    project = WorkspacesProject.from_path()

    target_set = resolve_targets(project, targets)

    if not target_set:
        theme.echo("<w>No workspaces selected.</w>")
        sys.exit(0)

    # Get a full map of dependees:
    dependee_map = _get_dependee_map(project, transitive=transitive, include_dev=dev)

    # Extract the relevant dependees:
    dependees_set = {dependee for target in target_set for dependee in dependee_map[target]}

    # Sort them from most depended on, to least depended on:
    sorted_dependees = [
        name
        for name, _ in sorted(dependee_map.items(), key=lambda item: -len(item[1]))
        if name in dependees_set or name in target_set
    ]

    if output == "csv":
        theme.echo(",".join(sorted_dependees), err=False)
        sys.exit(0)

    for dependee in sorted_dependees:
        theme.echo(dependee, err=False)
    sys.exit(0)


def _get_dependee_map(
    project: WorkspacesProject,
    transitive: bool = True,
    include_dev: bool = False,
) -> Dict[str, Set[str]]:
    """Get a mapping of workspaces to their dependees."""

    direct_map = defaultdict(set)
    for name, workspace in project.workspaces.items():
        for dependency in workspace.adapter.dependencies(include_dev=include_dev):
            direct_map[dependency].add(name)
    if not transitive:
        return dict(direct_map)

    @lru_cache(maxsize=None)
    def get_dependees(name: str):
        dependees = set(direct_map[name])
        for dependee in set(dependees):
            dependees |= get_dependees(dependee)
        return dependees

    return {name: get_dependees(name) for name in project.workspaces}
