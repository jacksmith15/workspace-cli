from workspaces.cli.theme import strip_tags
from workspaces.core.exceptions import WorkspacesError


class WorkspacesCLIError(WorkspacesError):
    def __init__(self, message: str, exit_code: int = 1):
        stripped = strip_tags(message)
        self.args = (stripped,)
        self.display = message
        self.exit_code = 1
