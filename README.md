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

## Development

Install dependencies:

```shell
pyenv shell 3.9.4  # Or other version >= 3.8
pre-commit install  # Configure commit hooks
poetry install  # Install Python dependencies
```

Run tests:

```shell
poetry run inv verify
```

# License
This project is distributed under the MIT license.
