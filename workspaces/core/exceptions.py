class WorkspacesError(Exception):
    """Base exception for workspaces package.

    Should only be raised directly for unexpected runtime errors.
    """


class WorkspacesProjectError(WorkspacesError):
    """Errors relating to workspaces project configuration."""


class WorkspacesProjectNotFoundError(WorkspacesProjectError):
    """The workspaces project could not be located."""


class WorkspacesProjectValidationError(WorkspacesProjectError):
    """The workspaces project file could not be parsed."""


class WorkspacesPluginError(WorkspacesError):
    """An error relating to an installed plugin."""


class WorkspacesWorkspaceError(WorkspacesError):
    """An error relating to a particular workspace."""


class WorkspacesWorkspaceImproperlyConfigured(WorkspacesWorkspaceError):
    """A workspace configuration is invalid."""
