import shlex
import subprocess
from pathlib import Path
from typing import List, Union

from tests.cli.commands.constants import WORKSPACE_ROOT


def run(command: Union[str, List[str]], cwd: Union[Path, str] = WORKSPACE_ROOT, assert_success: bool = True):
    """Run a command from within the test workspace root."""
    cwd = Path(cwd)
    if not cwd.is_absolute():
        cwd = WORKSPACE_ROOT / cwd

    def format_output(stdout: str, stderr: str) -> str:
        return "\n".join(
            [
                stdout.strip(),
                stderr.strip(),
            ]
        ).strip()

    if isinstance(command, str):
        command = shlex.split(command)

    try:
        result = subprocess.run(command, check=True, capture_output=True, cwd=cwd, text=True)
    except subprocess.CalledProcessError as exc:
        exc.text = format_output(exc.stdout, exc.stderr)  # type: ignore[attr-defined]
        if assert_success:
            assert not exc, exc.text  # type: ignore[attr-defined]
        raise exc
    result.text = format_output(result.stdout, result.stderr)  # type: ignore[attr-defined]
    return result
