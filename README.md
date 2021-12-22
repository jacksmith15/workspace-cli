# Workspace

**Workspace** streamlines management and adoption of mono-repositories, by providing a wrapper around multi-repo tooling.

It was initially implemented to manage Python projects, but can be extended to interpret other types of projects.

## Documentation

- [Home](https://jacksmith15.github.io/workspace-cli/)
    + [Installation](https://jacksmith15.github.io/workspace-cli/installation/)
    + [Configuration](https://jacksmith15.github.io/workspace-cli/configuration/)
    + [Basic usage](https://jacksmith15.github.io/workspace-cli/basic-usage/)
    + [Templates](https://jacksmith15.github.io/workspace-cli/templates/)
    + [Plugins](https://jacksmith15.github.io/workspace-cli/plugins/)
    + [FAQ](https://jacksmith15.github.io/workspace-cli/faq/)


## Development

Install dependencies:

```shell
pyenv shell 3.8.6  # Or other version >= 3.8
pre-commit install  # Configure commit hooks
poetry install -E poetry -E pipenv -E cookiecutter  # Install Python dependencies
```

Run tests:

```shell
poetry run inv verify
```

### Todos

- [ ] Experiment with non-Python workspaces
- [ ] More detailed plugin documentation
- [ ] Example workspaces
- [ ] Test output on shells with limited color support
- [ ] Labelling projects
- [ ] Project aliases

## License

This project is distributed under the MIT license.
