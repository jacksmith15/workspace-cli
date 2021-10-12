import sys
from pathlib import Path
from typing import Optional, Set, Tuple

import click

from workspace.cli import callbacks, theme
from workspace.core.models import Workspace


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
    """Reverse file paths to their respective projects.

    Accepts multiple arguments, and will output the deduplicated set of project names.
    """
    workspace = Workspace.from_path()

    results: Set[str] = set(filter(None, (_reverse_path(workspace, path) for path in paths)))
    if output == "csv":
        theme.echo(",".join(results), err=False)
        sys.exit(0)

    for result in results:
        theme.echo(result, err=False)
    sys.exit(0)


def _reverse_path(workspace: Workspace, path: Path) -> Optional[str]:
    relatives = {}
    path = path.resolve()
    for project in workspace.projects.values():
        try:
            relatives[project.name] = path.relative_to(project.resolved_path)
        except ValueError:
            continue
    if not relatives:
        return None
    return sorted(relatives.items(), key=lambda item: len(item[1].parents))[0][0]
