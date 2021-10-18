# Basic usage

## Start a new workspace

You can create a new workspace in the current working directory:

```terminal
$ workspace init
Created workspace at /current/working/directory.
```

> ℹ️ You can also specify the path to the workspace using the `--path` option.

This creates a file called `workspace.json`, which contains metadata about the workspace. This file marks the root directory of the workspace.

When detecting the active workspace, the CLI looks for a `workspace.json` file in the current directory first, followed by its parents.


> ℹ️ To display the current workspace path, run `workspace info`.


## Managing projects

### Creating a project from scratch

A workspace contains one or more projects. You can create a new project with `workspace new`:

```terminal
$ workspace new --type poetry libs/library-one
Created new project library-one at libs/library-one.
```

> ℹ️ This creates a [Poetry] project at the specified path. For other types of project, see [Project types](#project-types) below.

We can check this project exists by listing all projects in the workspace:

```terminal
$ workspace list

Name: library-one
Type: poetry
Path: /path/to/workspace/libs/library-one
Dependencies: []
```

> ℹ️ The name above was auto-generated from the directory name of the project. To specify a custom name, pass the `--name` flag to `workspace new` or `workspace add`.

### Adding an existing project

If you already have an existing project, add it to be tracked by the workspace:

```terminal
$ workspace add libs/library-two
Added new project library-two at libs/library-two.
```

> ℹ️ We didn't specify `--type` here, because the CLI will attempt to automatically detect from the available [types](#project-types). If the wrong type is detected, you can specify this explicitly.


### Removing a project

To stop tracking a workspace:

```terminal
$ workspace remove library-one
Stopped tracking projects:
  - library-one
```

> ⚠️ This will **not** delete anything by default. To delete the project directory, pass the `--delete` flag.

### Listing projects

To show information about all projects, use `workspace list`:

```terminal
$ workspace list

Name: library-one
Type: poetry
Path: /path/to/workspace/libs/library-one
Dependencies: []

Name: library-two
Type: poetry
Path: /path/to/workspace/libs/library-two
Dependencies: []
```

> 💡 This command (and others) support alternative output formats, including json. Run `workspace list --help` for more information.

> 💡 You can pass or pipe project names (or globbed names) to list a subset of projects. This can be combined with other commands which only output project names, to show more information about them.

## Project environments

Each project will have some environment, containing their dependencies. You can synchronise those environments for all projects at once, using:

```terminal
$ workspace sync --dev --parallel
Running poetry install

✔ library-two (0.8s)
✔ library-one (0.8s)
```

In the case of [Poetry] projects, this runs `poetry install` to prepare each project's [virtual environment](https://docs.python.org/3/tutorial/venv.html). Other [project types](#project-types) will perform other tasks.

## Running commands

Arbitrary commands can be run in every tracked project in parallel, ensuring that each uses their respective environments:

```terminal
$ workspace run -c 'pytest' --parallel

Running pytest

✔ library-two (0.5s)
✔ library-one (0.6s)
```


> 💡 The above command runs tests in parallel, which will only write command output if a command fails. To see the output of each command, omit the `--parallel` flag.

To run commands in specific projects, provide their names as positional arguments:

```terminal
$ workspace run -c 'pytest' library-one library-two
```

> 📖 `workspace run` supports piping a list of target project names, as well globbed names, for example:
> ```
> echo "library-*" | workspace run -c 'pytest'
> ```


## Dependency inference

Projects in a workspace will often depend on each other. This can be inspected with the appropriate commands:

```terminal
$ workspace dependencies library-two
library-two
library-one
```

```terminal
$ workspace dependees library-one
library-one
library-two
```


> ℹ️ Both of the above commands will traverse all transitive dependencies. To show only direct dependencies or dependees, pass the `--no-transitive` flag.

> 💡 Pass multiple inputs to output the union of results. As with `run`, piped and globbed arguments can be used.

To identify which project a particular file belongs to, use `workspace reverse`:

```terminal
$ workspace reverse libs/library-one/pyproject.toml
library-one
```

> 💡 Combine `run`, `dependees` and `reverse` to run tests on only the affected projects of a git diff:
> ```terminal
> git --no-pager diff --name-only |\
>     workspace reverse |\
>     workspace dependees |\
>     workspace run -c 'pytest'
> ```


## Project types

Every project in a workspace has a "type", which defines how the CLI interacts with that project and its environment. By default, two types are supported [Poetry] and [Pipenv], both of which manage Python project environments.

Additional types can be added via [plugins](./plugins.md).

[Poetry]: https://python-poetry.org/
[Pipenv]: https://pipenv-fork.readthedocs.io/en/latest/
