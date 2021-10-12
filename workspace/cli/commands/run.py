import sys
import time
from itertools import cycle
from typing import Dict, Iterable, List, NamedTuple, Tuple

import click

from workspace.cli import callbacks, theme
from workspace.cli.utils import resolve_specifiers
from workspace.core.models import Project, Workspace


@click.command()
@click.argument(
    "specifiers",
    nargs=-1,
    callback=callbacks.consume_stdin,
)
@click.option(
    "--command",
    "-c",
    type=str,
    required=True,
    help="The command to execute.",
)
@click.option(
    "--parallel/--no-parallel",
    "-p/ ",
    type=bool,
    default=False,
    help="Run the command in parallel.",
)
def run(specifiers: Tuple[str], command: str, parallel: bool = False):
    """Run a command in each project.

    If no specifiers are provided, the command will be run in all projects.
    """
    workspace = Workspace.from_path()

    if specifiers:
        target_set = resolve_specifiers(workspace, set(specifiers))
    else:
        target_set = set(workspace.projects)

    if not target_set:
        theme.echo("<w>No projects selected.</w>")
        sys.exit(0)

    projects = [workspace.projects[target] for target in target_set]
    sys.exit(_run_in_projects(projects, command, parallel=parallel))


def _run_in_projects(projects: List[Project], command: str, *, parallel: bool):
    """Run a command in provided projects, either in parallel or series."""
    if parallel:
        return _run_in_projects_parallel(projects, command)
    return _run_in_projects_series(projects, command)


def _run_in_projects_series(projects: List[Project], command: str) -> int:
    """Runs the command in each project in series.

    Command output is not captured.
    """
    exit_codes: Dict[str, int] = {}
    for project in projects:
        theme.echo(f"\nRunning <a><b>{command}</b></a>  (<b>{project.name}</b>)\n")
        result = project.adapter.run(command)
        exit_codes[project.name] = result.returncode

    failed = {name for name, code in exit_codes.items() if code}
    if failed:
        theme.echo("<e>Some projects failed</e>: " + ", ".join([f"<b>{name}</b>" for name in failed]))
    return get_exit_code(exit_codes.values())


def _run_in_projects_parallel(projects: List[Project], command: str) -> int:
    """Runs the command in each project in parallel.

    Command output is captured, and only displayed for projects which failed after all
    projects have finished.
    """
    theme.echo(f"\nRunning <a><b>{command}</b></a>\n")
    running = {project.name: project.adapter.popen(command) for project in projects}
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
