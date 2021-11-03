# Plugins

By default, two types of project are supported: `poetry` and `pipenv`. New types can be added by enabling plugins which contain _adapters_ for those project types.

A plugin is simply a Python module containing one or more subclasses of `workspace.core.adapter.Adapter`, which must implement its abstract methods.

## Adding plugins

Expand the following to see an example plugin for Python projects using `requirements.txt` files:

<details class="example"><summary>plugins/requirementstxt.py</summary>

```python
import os
import shlex
import subprocess
from typing import Set, Tuple

import requirements
from workspace.core.adapter import Adapter


class RequirementsTXTAdapter(Adapter, name="requirementstxt"):
    def validate(self):
        """Attempt to parse the requirements."""
        _ = self._requirements

    def run_args(self, command: str) -> Tuple[str, dict]:
        """Get modified command and kwargs that should be used when running inside the project."""
        command, kwargs = super().run_args(command)

        venv_path = self._ensure_virtualenv()
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = str(venv_path)
        env["PATH"] = f"{venv_path/'bin'}:{env['PATH']}"
        kwargs["env"] = env

        return command, kwargs

    def sync(self, include_dev: bool = True) -> subprocess.CompletedProcess:
        """Sync dependencies of the project."""
        command = ["pip", "install", "-r", "requirements.txt"]
        if include_dev:
            command.extend(["-r", "requirements-dev.txt"])
        return self.run(shlex.join(command))

    def dependencies(self, include_dev: bool = True) -> Set[str]:
        """Get other workspaces this project depends upon."""
        deps = self._requirements["default"]
        if include_dev:
            deps.extend(self._requirements["dev"])
        results = set()
        for dep in deps:
            if dep.editable:
                path = (self._project.resolved_path / dep.path).resolve()
                project = self._project.root.get_project_by_path(path)
                if project:
                    results.add(project.name)
        return results

    @property
    def _requirements(self):
        """Parse the requirements files."""
        return {
            "default": list(requirements.parse((self._project.resolved_path / "requirements.txt").read_text())),
            "dev": list(requirements.parse((self._project.resolved_path / "requirements-dev.txt").read_text())),
        }

    def _ensure_virtualenv(self):
        """Ensure virtualenv exists."""
        venv_path = self._project.resolved_path / ".venv"
        if not (venv_path / "bin/python").exists():
            subprocess.run(["python", "-m", "venv", venv_path], check=True)
        return venv_path
```

</details>

Provided the above example is on the `PYTHONPATH`, it can be enabled using

```terminal
$ workspace plugin add plugins.requirementstxt
Added plugin plugins.requirementstxt.

The following new project types are now available:
  - requirementstxt
```

Projects using `requirements.txt` files can then be added to the workspace.

## Showing currently enabled plugins

The currently enabled plugins can be shown using:

```terminal
$ workspace plugin list
plugins.requirementstxt
```

## Disabling plugins

Plugins can be disabled using:

```terminal
$ workspace plugin remove plugins.requirementstxt
Removed plugin plugins.requirementstxt.
```

> ⚠️ Ensure that no projects use types enabled by a plugin before disabling it, or the workspace will not be able to interact with the project.
