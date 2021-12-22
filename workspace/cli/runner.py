import time
from itertools import cycle
from typing import Dict, Iterable, List, NamedTuple, Tuple

import click

from workspace.cli import theme
from workspace.core.models import Project


def run(project_commands: List[Tuple[Project, str]], *, parallel: bool) -> int:
    """Run each command in each project, in series or parallel."""
    if parallel:
        return _run_in_parallel(project_commands)
    return _run_in_series(project_commands)


def _run_in_series(project_commands: List[Tuple[Project, str]]) -> int:
    """Run each command in each project in series.

    Command output is not captured.
    """
    exit_codes: Dict[str, int] = {}
    for project, command in project_commands:
        theme.echo(f"\nRunning <a><b>{command}</b></a>  (<b>{project.name}</b>)\n")
        result = project.adapter.run(command)
        exit_codes[project.name] = result.returncode

    failed = {name for name, code in exit_codes.items() if code}

    theme.echo("")
    if failed:
        theme.echo("<e>Some projects failed</e>: " + ", ".join([f"<b>{name}</b>" for name in failed]))
    return _get_exit_code(exit_codes.values())


def _run_in_parallel(project_commands: List[Tuple[Project, str]]) -> int:
    """Run each command in each project in parallel.

    Command output is captured, and only displayed for projects which failed after all
    projects have finished.
    """
    commands = {command for _, command in project_commands}
    if len(commands) == 1:
        command_repr = commands.pop()
    else:
        command_repr = "[various commands]"
    theme.echo(f"\nRunning <a><b>{command_repr}</b></a>\n")
    running = {project.name: project.adapter.popen(command) for project, command in project_commands}
    complete: Dict[str, Result] = {}
    spinner = Spinner()
    timer = Timer()
    max_name_length = max([len(name) for name in running])
    while running:
        for name, popen in running.copy().items():
            exit_code = popen.poll()
            theme.echo(
                f"{next(spinner)} <a>Running ({next(timer)})</a>: " + ", ".join([f"<b>{name}</b>" for name in running]),
                nl=False,
                rewrite=True,
            )
            if exit_code is None:
                continue
            stdout, stderr = popen.communicate()
            del running[name]
            complete[name] = Result(exit_code=exit_code, stdout=stdout, stderr=stderr)
            if exit_code != 0:
                theme.echo(f"<e>✘ {name.ljust(max_name_length)} ({next(timer)})</e>", rewrite=True)
            else:
                theme.echo(f"<s>✔ {name.ljust(max_name_length)} ({next(timer)})</s>", rewrite=True)

    theme.echo("")
    for name, result in complete.items():
        if not result.success:
            theme.echo(f"<e><b>{name}</b> failed with exit code <b>{exit_code}</b></e>:")
            click.echo(result.output)  # Don't try to format subprocess output

    return _get_exit_code({result.exit_code for result in complete.values()})


def _get_exit_code(exit_codes: Iterable[int]) -> int:
    """Reduce a set of exit codes to the absolute value."""
    return sorted(exit_codes, key=lambda code: abs(code), reverse=True)[0]


def Spinner(chars: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏", fps: float = 10):
    """A spinner for showing progress."""
    frames = cycle(chars)
    current_frame = next(frames)
    last_update = time.monotonic()
    delay = 1 / fps
    while True:
        now = time.monotonic()
        if now - last_update > delay:
            last_update = now
            current_frame = next(frames)
        yield current_frame


def Timer():
    """A timer which shows total time elapsed on each iteration."""
    start = time.monotonic()
    while True:
        yield f"{time.monotonic() - start:.1f}s"


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
