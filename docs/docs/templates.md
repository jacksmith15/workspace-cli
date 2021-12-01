# Templates

The CLI has in-built support for using custom [cookiecutter templates](https://github.com/cookiecutter/cookiecutter) to create new projects in your workspace.

## Template path

Given a `templates/` directory contains some templates:

```
WORKSPACE_ROOT/
    templates/
        library-template/
        application-template/
    workspace.json
```

Make these templates available by adding the directory to the _template path_:

```terminal
$ workspace template path add templates/       
Added templates to available template directories.
```

> 💡 Any templates added to the directory above will automatically be available to the workspace.

Inspect the available templates with:

```terminal
$ workspace template list               
library-template        templates/library-template
application-template    templates/application-template
```

> ℹ️ Multiple directories can be added to the template path. To inspect the current template path, use `workspace info`.

## Using templates

Available templates can be used to create a new projects:

```terminal
$ workspaces new --template library-template libs/my-new-library
Created new project my-new-library at libs/my-new-library.
```

> 💡 Ensure cookiecutter is installed with `pip install workspace-cli[cookiecutter]`.

## Default variables

Some additional variables can be automatically made available to project templates:

- `{{ workspace_project_path }}` is the relative path of the project from the workspace root.
- `{{ workspace_project_name }}` is the name of the project in the workspace.

To make these available, include them in the template's `cookiecutter.json` file, e.g.

```json
{
    "workspace_project_path": null,
    "workspace_project_name": null
}
```

> ⚠️ Encoding these in a project creates coupling between the project and the workspace.
