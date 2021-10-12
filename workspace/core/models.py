from __future__ import annotations

import importlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

import jsonschema

from workspace.core import exceptions
from workspace.core.adapter import Adapter, get_adapter
from workspace.core.settings import get_settings
from workspace.core.templates import Templates

_PROJECT_CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["projects"],
    "properties": {
        "projects": {
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
class Workspace:
    path: Path
    projects: Dict[str, Project]
    plugins: Optional[List[str]] = None
    template_path: Optional[List[str]] = None

    @classmethod
    def from_path(cls, path: Union[Path, str] = None) -> Workspace:
        path = path or Path.cwd()
        path = Path(path) if isinstance(path, str) else path
        path = path.resolve()
        if path.is_file():
            return cls.load(path)
        for directory in [path, *path.parents]:
            filepath = directory / get_settings().filename
            if filepath.exists() and filepath.is_file():
                return cls.load(filepath)
        raise exceptions.WorkspaceNotFoundError(
            f"No workspace file {get_settings().filename!r} found in '{path}' or its parents."
        )

    @classmethod
    def load(cls, path: Path) -> Workspace:
        text = path.read_text()
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            raise exceptions.WorkspaceValidationError(f"Workspace file at '{path}' is not valid JSON.")

        try:
            jsonschema.validate(
                schema=_PROJECT_CONFIG_SCHEMA,
                instance=body,
            )
        except jsonschema.ValidationError as exc:
            raise exceptions.WorkspaceValidationError(f"Invalid workspace file at '{path}': {exc.message}")

        kwargs = {"path": path.parent, "projects": {}}
        if "plugins" in body:
            kwargs["plugins"] = body["plugins"]
        if "template_path" in body:
            kwargs["template_path"] = body["template_path"]

        workspace = cls(**kwargs)  # type: ignore[arg-type]
        for name, project in body.get("projects", {}).items():
            workspace.set_project(name, **project)
        workspace._load_plugins()
        return workspace

    @property
    def templates(self) -> Templates:
        return Templates(self)

    def get_project_by_path(self, path: Path) -> Optional[Project]:
        path = path.resolve()
        for project in self.projects.values():
            if project.resolved_path == path:
                return project
        return None

    def set_project(self, name: str, path: str, type: str) -> Project:
        project = Project(name=name, root=self, path=path, type=type)
        self.projects[name] = project
        return project

    def flush(self) -> None:
        output: dict = {
            "projects": {
                project.name: {
                    "path": project.path,
                    "type": project.type,
                }
                for project in self.projects.values()
            }
        }
        if self.plugins is not None:
            output["plugins"] = self.plugins
        if self.template_path is not None:
            output["template_path"] = self.template_path
        with open(self.path / get_settings().filename, "w", encoding="utf-8") as file:
            file.write(json.dumps(output, sort_keys=True, indent=2))

    def _load_plugins(self) -> None:
        for plugin in self.plugins or []:
            try:
                importlib.import_module(plugin)
            except ModuleNotFoundError:
                raise exceptions.WorkspacePluginError(f"Could not find configured plugin {plugin!r}.")


@dataclass
class Project:
    """A particular project within a workspace."""

    name: str
    root: Workspace = field(repr=False)
    path: str
    type: str
    # options (type-specific)

    @property
    def resolved_path(self) -> Path:
        return (self.root.path / Path(self.path)).resolve()

    @property
    def adapter(self) -> Adapter:
        return get_adapter(self.type)(self)
