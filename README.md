# Workspaces CLI

Manage interdependent projects as workspaces.

## Installation

This project is not currently packaged and so must be installed manually.

Clone the project with the following command:
```
git clone https://github.com/jacksmith15/workspaces.git
```

## Usage

Initialise a workspaces project:

```bash
cd $PROJECT_ROOT
workspaces init
```

> :information_source: This creates a `workspaces.json` file in the root directory of your project. The `workspaces.json` file tracks information about workspaces in your project.

Create a new workspace:

```bash
workspaces new --type poetry libs/library-one
```

> :information_source: This creates a new blank poetry project at `libs/library-one`, and tracks it as a workspace.

You can also track an existing project as a workspace:

```bash
workspaces add libs/library-two
```

You can run a command in every workspace, ensuring that each workspace uses their respective isolated virtualenvs:

```bash
workspaces run -c pytest
```

Or specify the workspaces to run in:

```bash
workspaces run library-one -c pytest
```

> :information_source: `workspaces run` supports piping a list of target workspace names, as well as workspace names with globs, e.g. `echo "library-*" | workspaces run -c pytest`.
>

### Dependency inference

If one workspace depends on another (usually via an [editable dependency](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs)), you can inspect the dependees of a particular workspace:

```bash
workspaces dependees library-one
# library-one
# library-two
```

Combining the above with `run`, you can easily re-run tests on the affected workspaces:

```bash
workspaces dependees library-one | workspaces run -c pytest
```

You can also check which workspace (if any) a particular file, or set of files, belongs to:

```bash
workspaces reverse /path/to/project/lib/library-one/foo.py
# library-one
```

Combining `run`, `dependees` and `reverse`, you can test affected workspaces based on a git diff:

```bash
git --no-pager diff --name-only | workspaces reverse | workspaces dependees | workspaces run -c 'pytest'
```

### Templates

The CLI has in-built support for using custom [cookiecutter templates](https://github.com/cookiecutter/cookiecutter) on workspaces in your project.

You can specify a path to your templates using:

```bash
workspaces template path add templates/
```

Given the `templates/` directory contains these templates:

```
PROJECT_ROOT/
    templates/
        library-template/
        application-template/
    workspaces.json
```

You can inspect the available templates with:

```bash
workspaces template list
# library-template
# application-template
```

And use a template to create a new workspace with:

```bash
workspaces new --template library-template libs/my-new-library
```

> :information_source: Ensure cookiecutter is installed with `pip install workspaces-cli[cookiecutter]`.


### Plugins

By default, `workspaces` supports two types of workspace: `poetry` and `pipenv`. New types can be registered by enabling plugins which contain _adapters_ for those new types.

A plugin is simply a Python module containing one or more subclasses of `workspaces.core.adapter.Adapter`, which implement its abstract methods.

Expand the following to see an example plugin for Python projects using `requirements.txt` files:

<details><summary>plugins/requirementstxt.py</summary>

```python
import os
import shlex
import subprocess
from typing import Set, Tuple

import requirements
from workspaces.core.adapter import Adapter


class RequirementsTXTAdapter(Adapter, name="requirementstxt"):
    def validate(self):
        """Attempt to parse the requirements."""
        _ = self._requirements

    def run_args(self, command: str) -> Tuple[str, dict]:
        """Get modified command and kwargs that should be used when running inside the workspace."""
        command, kwargs = super().run_args(command)

        venv_path = self._ensure_virtualenv()
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = str(venv_path)
        env["PATH"] = f"{venv_path/'bin'}:{env['PATH']}"
        kwargs["env"] = env

        return command, kwargs

    def sync(self, include_dev: bool = True) -> subprocess.CompletedProcess:
        """Sync dependencies of the workspace."""
        command = ["pip", "install", "-r", "requirements.txt"]
        if include_dev:
            command.extend(["-r", "requirements-dev.txt"])
        return self.run(shlex.join(command))

    def dependencies(self, include_dev: bool = True) -> Set[str]:
        """Get other workspaces this workspace depends upon."""
        deps = self._requirements["default"]
        if include_dev:
            deps.extend(self._requirements["dev"])
        results = set()
        for dep in deps:
            if dep.editable:
                path = (self._workspace.resolved_path / dep.path).resolve()
                workspace = self._workspace.root.get_workspace_by_path(path)
                if workspace:
                    results.add(workspace.name)
        return results

    @property
    def _requirements(self):
        """Parse the requirements files."""
        return {
            "default": list(requirements.parse((self._workspace.resolved_path / "requirements.txt").read_text())),
            "dev": list(requirements.parse((self._workspace.resolved_path / "requirements-dev.txt").read_text())),
        }

    def _ensure_virtualenv(self):
        """Ensure virtualenv exists."""
        venv_path = self._workspace.resolved_path / ".venv"
        if not (venv_path / "bin/python").exists():
            subprocess.run(["python", "-m", "venv", venv_path], check=True)
        return venv_path
```

</details>

Given such a plugin is available on your `PYTHONPATH`, you can enable it using

```bash
workspaces plugin add plugins.requirementstxt
```

You are then able to add projects of this type by specifying `--type requirementstxt`.


## Development

Install dependencies:

```shell
pyenv shell 3.8.6  # Or other version >= 3.8
pre-commit install  # Configure commit hooks
poetry install  # Install Python dependencies
```

Run tests:

```shell
poetry run inv verify
```

# License
This project is distributed under the MIT license.
