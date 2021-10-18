# Configuration

## Global configuration

Global configuration is read from environment variables.

| Name  | Default | Description |
| --- | --- | --- |
| `WORKSPACE_FILENAME` | `workspace.json` | Filename to search for when detecting workspaces. |


## Workspace configuration

The contents of `workspace.json` is primarily configured via CLI. It supports the following fields:

| Field | Required | Type | Description |
| --- | --- | --- | --- |
| `projects` | yes | object | A mapping of name to project metadata. |
| `plugins` | no | array | List of enabled plugins as Python module paths. |
| `template_path` | no | array | List of paths to detect templates. |

