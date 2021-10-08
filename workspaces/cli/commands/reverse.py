import sys
from pathlib import Path
from typing import Optional, Set, Tuple

import click

from workspaces.cli import callbacks, theme
from workspaces.core.models import WorkspacesProject


@click.command()
@click.argument(
    "paths",
    nargs=-1,
    callback=callbacks.consume_stdin,
    type=click.Path(exists=False, file_okay=True, dir_okay=True, path_type=Path),
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(("lines", "csv")),
    help="Select the output format.",
    default="lines",
)
def reverse(paths: Tuple[Path, ...], output: str = "lines"):
    """Reverse file paths to their respective workspaces.

    Accepts multiple arguments, and will output the deduplicated set of reversed workspaces.
    """
    project = WorkspacesProject.from_path()

    results: Set[str] = set(filter(None, (_reverse_path(project, path) for path in paths)))
    if output == "csv":
        theme.echo(",".join(results), err=False)
        sys.exit(0)

    for result in results:
        theme.echo(result, err=False)
    sys.exit(0)


def _reverse_path(project: WorkspacesProject, path: Path) -> Optional[str]:
    relatives = {}
    path = path.resolve()
    for workspace in project.workspaces.values():
        try:
            relatives[workspace.name] = path.relative_to(workspace.resolved_path)
        except ValueError:
            continue
    if not relatives:
        return None
    return sorted(relatives.items(), key=lambda item: len(item[1].parents))[0][0]
