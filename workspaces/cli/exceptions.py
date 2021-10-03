from workspaces.cli.theme import strip_tags
from workspaces.core.exceptions import WorkspacesError


class WorkspacesCLIError(WorkspacesError):
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = 1

    def __repr__(self):
        return strip_tags(super().__repr__())

    def __str__(self):
        return strip_tags(super().__str__())

    @property
    def display(self):
        return super().__str__()
