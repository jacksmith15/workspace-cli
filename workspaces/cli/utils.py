from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, Optional, Set

from workspaces.core.adapter import get_adapters
from workspaces.core.models import Workspace, WorkspacesProject


def resolve_targets(project: WorkspacesProject, targets: Iterable[str]) -> Set[str]:
    result = set()
    for target in targets:
        target = target.strip()
        for workspace in project.workspaces:
            if workspace in result:
                continue
            if target == workspace:
                result.add(workspace)
                continue
            if fnmatch(workspace, target):
                result.add(workspace)
    for name in result:
        project.workspaces[name].adapter.validate()
    return result


def detect_type(project: WorkspacesProject, path: Path) -> Optional[str]:
    for type_name in get_adapters():
        workspace = Workspace(
            name="_",
            path=str(Path.cwd().relative_to(project.path) / path),
            type=type_name,
            root=project,
        )
        try:
            workspace.adapter.validate()
            return type_name
        except:
            continue
    return None
