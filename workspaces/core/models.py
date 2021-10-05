from __future__ import annotations

import importlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

import jsonschema

from workspaces.core.adapter import Adapter, get_adapter
from workspaces.core.exceptions import WorkspacesError
from workspaces.core.settings import get_settings
from workspaces.core.templates import Templates

_PROJECT_CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["workspaces"],
    "properties": {
        "workspaces": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "type": {"type": "string"}},
            },
        },
        "plugins": {"type": "array", "items": {"type": "string"}},
        "template_path": {"type": "array", "items": {"type": "string"}},
    },
}


@dataclass
class WorkspacesProject:
    path: Path
    workspaces: Dict[str, Workspace]
    plugins: Optional[List[str]] = None
    template_path: Optional[List[str]] = None

    @classmethod
    def from_path(cls, path: Union[Path, str] = None) -> WorkspacesProject:
        path = path or Path.cwd()
        path = Path(path) if isinstance(path, str) else path
        path = path.resolve()
        if path.is_file():
            return cls.load(path)
        for directory in [path, *path.parents]:
            filepath = directory / get_settings().project_filename
            if filepath.exists() and filepath.is_file():
                return cls.load(filepath)
        raise WorkspacesError(
            f"No workspaces project file {get_settings().project_filename!r} found in '{path}' or its parents."
        )

    @classmethod
    def load(cls, path: Path) -> WorkspacesProject:
        text = path.read_text()
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            raise WorkspacesError(f"Workspaces project file at '{path}' is not valid JSON.")

        try:
            jsonschema.validate(
                schema=_PROJECT_CONFIG_SCHEMA,
                instance=body,
            )
        except jsonschema.ValidationError as exc:
            raise WorkspacesError(f"Invalid workspaces project file at '{path}': {exc.message}")

        kwargs = {"path": path.parent, "workspaces": {}}
        if "plugins" in body:
            kwargs["plugins"] = body["plugins"]
        if "template_path" in body:
            kwargs["template_path"] = body["template_path"]

        project = cls(**kwargs)  # type: ignore[arg-type]
        for name, workspace in body.get("workspaces", {}).items():
            project.set_workspace(name, **workspace)
        project._load_plugins()
        return project

    @property
    def templates(self):
        return Templates(self)

    def get_workspace_by_path(self, path: Path) -> Optional[Workspace]:
        path = path.resolve()
        for workspace in self.workspaces.values():
            if workspace.resolved_path == path:
                return workspace
        return None

    def set_workspace(self, name: str, path: str, type: str) -> Workspace:
        workspace = Workspace(name=name, root=self, path=path, type=type)
        self.workspaces[name] = workspace
        return workspace

    def flush(self):
        output = {
            "workspaces": {
                workspace.name: {
                    "path": workspace.path,
                    "type": workspace.type,
                }
                for workspace in self.workspaces.values()
            }
        }
        if self.plugins is not None:
            output["plugins"] = self.plugins
        if self.template_path is not None:
            output["template_path"] = self.template_path
        with open(self.path / get_settings().project_filename, "w", encoding="utf-8") as file:
            file.write(json.dumps(output, sort_keys=True, indent=2))

    def _load_plugins(self):
        for plugin in self.plugins or []:
            try:
                importlib.import_module(plugin)
            except ModuleNotFoundError:
                raise WorkspacesError(f"Could not find configured plugin {plugin!r}")


@dataclass
class Workspace:
    name: str
    root: WorkspacesProject = field(repr=False)
    path: str
    type: str
    # options (type-specific)

    @property
    def resolved_path(self) -> Path:
        return (self.root.path / Path(self.path)).resolve()

    @property
    def adapter(self) -> Adapter:
        return get_adapter(self.type)(self)
