import sys
import time
from itertools import cycle
from typing import Dict, Iterable, List, NamedTuple, Tuple

import click

from workspaces.cli import callbacks, theme
from workspaces.cli.utils import resolve_targets
from workspaces.core.models import Workspace, WorkspacesProject


@click.command()
@click.argument(
    "targets",
    nargs=-1,
    callback=callbacks.consume_stdin,
)
@click.option(
    "--command",
    "-c",
    type=str,
    required=True,
    help="The command to execute in the target workspaces.",
)
@click.option(
    "--parallel/--no-parallel",
    "-p/ ",
    type=bool,
    default=False,
    help="Run the commands in each target workspace in parallel.",
)
def run(targets: Tuple[str], command: str, parallel: bool = False):
    """Run a command in each target workspace."""
    project = WorkspacesProject.from_path()

    if targets:
        target_set = resolve_targets(project, set(targets))
    else:
        target_set = set(project.workspaces)

    if not target_set:
        theme.echo("<w>No workspaces selected.</w>")
        sys.exit(0)

    workspaces = [project.workspaces[target] for target in target_set]
    sys.exit(_run_in_workspaces(workspaces, command, parallel=parallel))


def _run_in_workspaces(workspaces: List[Workspace], command: str, *, parallel: bool):
    """Run a command in provided workspaces, either in parallel or series."""
    if parallel:
        return _run_in_workspaces_parallel(workspaces, command)
    return _run_in_workspaces_series(workspaces, command)


def _run_in_workspaces_series(workspaces: List[Workspace], command: str) -> int:
    """Runs the command in each workspace in series.

    Command output is not captured.
    """
    exit_codes: Dict[str, int] = {}
    for workspace in workspaces:
        theme.echo(f"\nRunning <a><b>{command}</b></a>  (<b>{workspace.name}</b>)\n")
        result = workspace.adapter.run(command)
        exit_codes[workspace.name] = result.returncode

    failed = {name for name, code in exit_codes.items() if code}
    if failed:
        theme.echo("<e>Some workspaces failed</e>: " + ", ".join([f"<b>{name}</b>" for name in failed]))
    return get_exit_code(exit_codes.values())


def _run_in_workspaces_parallel(workspaces: List[Workspace], command: str) -> int:
    """Runs the command in each workspace in parallel.

    Command output is captured, and only displayed for workspaces which failed after all
    workspaces have finished.
    """
    theme.echo(f"\nRunning <a><b>{command}</b></a>\n")
    running = {workspace.name: workspace.adapter.popen(command) for workspace in workspaces}
    complete: Dict[str, Result] = {}
    spinner = Spinner()
    while running:
        for name, popen in running.copy().items():
            exit_code = popen.poll()
            theme.echo(
                f"{next(spinner)} <a>Running</a>: " + ", ".join([f"<b>{name}</b>" for name in running]),
                nl=False,
                rewrite=True,
            )
            if exit_code is None:
                continue
            stdout, stderr = popen.communicate()
            del running[name]
            complete[name] = Result(exit_code=exit_code, stdout=stdout, stderr=stderr)
            if exit_code != 0:
                theme.echo(f"<e>✘ {name}</e>", rewrite=True)
            else:
                theme.echo(f"<s>✔ {name}</s>", rewrite=True)
        time.sleep(100 / 1000)  # 100ms

    theme.echo("")
    for name, result in complete.items():
        if not result.success:
            theme.echo(f"<e><b>{name}</b> failed with exit code <b>{exit_code}</b></e>:")
            theme.echo(result.output)

    return get_exit_code({result.exit_code for result in complete.values()})


def get_exit_code(exit_codes: Iterable[int]) -> int:
    """Reduce a set of exit codes to the greatest magnitude."""
    return sorted(exit_codes, key=lambda code: abs(code), reverse=True)[0]


class Spinner:
    """A spinner for showing progress."""

    def __init__(self, chars: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏", delay: float = 0.1):
        self._iter = cycle(chars)
        self._last = time.monotonic()
        self._current = next(self._iter)
        self._delay = delay

    def __iter__(self):
        return self

    def __next__(self):
        if time.monotonic() - self._last > self._delay:
            self._last = time.monotonic()
            self._current = next(self._iter)
        return self._current


class Result(NamedTuple):
    """Result of a subprocess."""

    exit_code: int
    stdout: str
    stderr: str

    @property
    def output(self) -> str:
        return "\n".join([self.stdout, self.stderr])

    @property
    def success(self) -> bool:
        return self.exit_code == 0
