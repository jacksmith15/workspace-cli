import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, Optional, Set

from workspace.core.adapter import get_adapters
from workspace.core.models import Project, Workspace


def resolve_specifiers(workspace: Workspace, specifiers: Iterable[str]) -> Set[str]:
    """Extract project names from given specifiers.

    Specifiers can be exact project names, or glob patterns.
    """
    result = set()
    for specifier in specifiers:
        specifier = specifier.strip()
        for project in workspace.projects:
            if project in result:
                continue
            if specifier == project:
                result.add(project)
                continue
            try:
                if fnmatch(project, specifier):
                    result.add(project)
            except re.error:
                continue
    for name in result:
        workspace.projects[name].adapter.validate()
    return result


def detect_type(workspace: Workspace, path: Path) -> Optional[str]:
    """Detect the type of a project at the given path."""
    for type_name in get_adapters():
        project = Project(
            name="_",
            path=str(Path.cwd().relative_to(workspace.path) / path),
            type=type_name,
            root=workspace,
        )
        try:
            project.adapter.validate()
            return type_name
        except:
            continue
    return None
