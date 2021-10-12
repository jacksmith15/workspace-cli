class WorkspaceBaseError(Exception):
    """Base exception for workspaces package.

    Should only be raised directly for unexpected runtime errors.
    """


class WorkspaceError(WorkspaceBaseError):
    """Errors relating to a particular workspace configuration."""


class WorkspaceNotFoundError(WorkspaceError):
    """A workspace file could not be located."""


class WorkspaceValidationError(WorkspaceError):
    """The workspace file could not be parsed."""


class WorkspacePluginError(WorkspaceBaseError):
    """An error relating to an installed plugin."""


class WorkspaceProjectError(WorkspaceBaseError):
    """An error relating to a particular project."""


class WorkspaceProjectImproperlyConfigured(WorkspaceProjectError):
    """A project configuration is invalid."""


class WorkspaceTemplateError(WorkspaceBaseError):
    """An error relating to templates."""
