# Workspace

**Workspace** streamlines management and adoption of mono-repositories, by providing a wrapper around multi-repo tooling.

It was initially implemented to manage Python projects, but can be extended to interpret other types of projects.

## Documentation

- [Home](./docs/docs/index.md)
    + [Installation](./docs/docs/installation.md)
    + [Configuration](./docs/docs/configuration.md)
    + [Basic usage](./docs/docs/basic-usage.md)
    + [Templates](./docs/docs/templates.md)
    + [Plugins](./docs/docs/plugins.md)
    + [FAQ](./docs/docs/faq.md)


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
- [ ] More detailed plugin documentation
- [ ] Example workspaces
- [ ] Test output on shells with limited color support
- [ ] Labelling projects
- [ ] Project aliases

## License

This project is distributed under the MIT license.
