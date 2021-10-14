# Workspace CLI

Manage interdependent projects in a **workspace**.

## Installation

This project is not currently packaged and so must be installed manually.

Clone the project with the following command:
```
git clone https://github.com/jacksmith15/workspace-cli.git
```

## Usage

Initialise a workspace:

```bash
cd $WORKSPACE_ROOT
workspace init
```

> :information_source: This creates a `workspace.json` file, which marks the root directory of the workspace, and contains metadata.

Create a new project:

```bash
workspace new --type poetry libs/library-one
```

> :information_source: This creates a new blank poetry project at `libs/library-one`, and tracks it in the workspace.

You can also track an existing project in the workspace:

```bash
workspace add libs/library-two
```

You can run a command in every tracked project, ensuring that each uses their respective isolated virtual environments:

```bash
workspace run -c pytest
```

Or specify a subset of projects to run the command in:

```bash
workspace run library-one -c pytest
```

> :information_source: `workspace run` supports piping a list of target project names, as well globbed names, e.g. `echo "library-*" | workspace run -c pytest`.


### Dependency inference

Sometimes one project depends on another (usually via an [editable dependency](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs)). You can inspect the dependees of a particular project:

```bash
workspace dependees library-one
# library-one
# library-two
```

Combining the above with `run`, you can easily run a command in just a project and its dependees (i.e. to test after a change):

```bash
workspace dependees library-one | workspace run -c pytest
```

You can also check which project a particular file or set of files, belongs to:

```bash
workspace reverse libs/library-one/foo.py
# library-one
```

Combining `run`, `dependees` and `reverse`, you can perform complex tasks, such as running tests for all affected projects in a git diff:

```bash
git --no-pager diff --name-only | workspace reverse | workspace dependees | workspace run -c 'pytest'
```

### Templates

The CLI has in-built support for using custom [cookiecutter templates](https://github.com/cookiecutter/cookiecutter) to create new projects in your workspace.

You can specify a path to your templates using:

```bash
workspace template path add templates/
```

Given the `templates/` directory contains these templates:

```
WORKSPACE_ROOT/
    templates/
        library-template/
        application-template/
    workspace.json
```

You can inspect the available templates with:

```bash
workspace template list
# library-template
# application-template
```

And use a template to create a new project with:

```bash
workspaces new --template library-template libs/my-new-library
```

> :information_source: Ensure cookiecutter is installed with `pip install workspace-cli[cookiecutter]`.


### Plugins

By default, `workspace` supports two types of project: `poetry` and `pipenv`. New types can be registered by enabling plugins which contain _adapters_ for those new project types.

A plugin is simply a Python module containing one or more subclasses of `workspace.core.adapter.Adapter`, which implement its abstract methods.

Expand the following to see an example plugin for Python projects using `requirements.txt` files:

<details><summary>plugins/requirementstxt.py</summary>

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

Given such a plugin is available on your `PYTHONPATH`, you can enable it using

```bash
workspace plugin add plugins.requirementstxt
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

### Todos

- [ ] Experiment with non-Python workspaces
- [ ] Detailed documentation, with common patterns
- [ ] Easier set-up of local plugins (?)
- [ ] Test output on shells with limited color support
- [ ] "Why not X" section in README

# License
This project is distributed under the MIT license.
