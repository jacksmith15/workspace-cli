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
