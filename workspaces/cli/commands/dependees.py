import sys
from collections import defaultdict
from functools import lru_cache
from typing import Dict, Set, Tuple

import click

from workspaces.cli import theme
from workspaces.cli.utils import resolve_targets
from workspaces.core.models import WorkspacesProject


@click.command()
@click.argument(
    "targets",
    nargs=-1,
)
@click.option("--no-transitive", type=bool, default=False, help="Only show direct dependees.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(("lines", "csv")),
    help="Select the output format.",
    default="lines",
)
@click.option(
    "--dev",
    "-d",
    type=bool,
    help="Include development dependencies.",
    default=False,
)
def dependees(targets: Tuple[str, ...], no_transitive: bool = False, output: str = "lines", dev: bool = False):
    """Runs command ARGS in each target workspace tracked by the current project."""
    project = WorkspacesProject.from_path()

    target_set = resolve_targets(project, targets)

    unexpected = target_set - set(project.workspaces)
    if unexpected:
        unexpected_output = ", ".join((theme.error(name, accent=True) for name in unexpected))
        click.echo(theme.error(f"Unknown workspace{'s' if len(unexpected) > 1 else ''}: {unexpected_output}"), err=True)
        sys.exit(1)

    if not target_set:
        click.echo(theme.attention("No workspaces selected."))
        sys.exit(0)

    # Get a full map of dependees:
    dependee_map = _get_dependee_map(project, transitive=not no_transitive, include_dev=dev)

    # Extract the relevant dependees:
    dependees_set = {dependee for target in target_set for dependee in dependee_map[target]}

    # Sort them from most depended on, to least depended on:
    sorted_dependees = [
        name
        for name, _ in sorted(dependee_map.items(), key=lambda item: -len(item[1]))
        if name in dependees_set or name in target_set
    ]

    if output == "csv":
        click.echo(theme.text(",".join(sorted_dependees)))
        sys.exit(0)

    for dependee in sorted_dependees:
        click.echo(theme.text(dependee))
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
