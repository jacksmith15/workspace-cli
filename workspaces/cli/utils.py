from fnmatch import fnmatch
from typing import Iterable, Set

from workspaces.core.models import WorkspacesProject


def resolve_targets(project: WorkspacesProject, targets: Iterable[str]) -> Set[str]:
    result = set()
    for target in targets:
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
