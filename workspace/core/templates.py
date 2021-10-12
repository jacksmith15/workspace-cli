from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, List, Set

from workspace.core.exceptions import WorkspaceTemplateError

if TYPE_CHECKING:
    from workspace.core.models import Workspace  # pragma: no cover


@dataclass
class Templates:
    workspace: Workspace

    @property
    def template_paths(self) -> List[Path]:
        if not self.workspace.template_path:
            return []
        return [self.workspace.path / Path(path) for path in self.workspace.template_path]

    def __iter__(self) -> Iterator[Path]:
        seen: Set[str] = set()
        for template_path in self.template_paths:
            for path in template_path.glob("*/cookiecutter.json"):
                if path.parent.name in seen:
                    continue
                seen.add(path.parent.name)
                yield path.parent

    def __getitem__(self, template_name: str) -> Path:
        for path in self.template_paths:
            target = path / template_name / "cookiecutter.json"
            if target.exists() and target.is_file():
                return target.parent
        raise KeyError(template_name)

    def __contains__(self, template_name: str) -> bool:
        try:
            self[template_name]
            return True
        except KeyError:
            return False

    def create(self, template_name: str, path: Path):
        try:
            template_path = self[template_name]
        except KeyError:
            raise WorkspaceTemplateError(f"Template not found: {template_name}")
        try:
            from cookiecutter.main import cookiecutter
        except ImportError:
            raise WorkspaceTemplateError(
                "Cookiecutter is not installed - run 'pip install workspace-cli[cookiecutter]'."
            )
        cookiecutter(
            template=str(template_path),
            output_dir=path.parent,
            extra_context=_build_context(template_path, path),
            no_input=True,
        )


def _build_context(template_path: Path, target_directory: Path) -> str:
    """Build the cookiecutter context.

    We need to combine the target directory and prompt the user for all other fields. By
    default cookiecutter is all or nothing when it comes to user input, which is no good,
    because it would be easy to accidentally enter a value which conflicts with the already
    provided directory name.

    As such, we do our own prompt logic (heavily inspired by cookiecutter's).
    """
    from cookiecutter.generate import generate_context

    # Get the field name used for the template's directory
    directory_field = _extract_directory_field(template_path)

    # Prompt user to provide any other fields
    context = generate_context(
        context_file=template_path / "cookiecutter.json",
    )
    extra_context = _prompt_for_config(context, {directory_field: target_directory.name})

    # Return the rendered context
    return extra_context


def _prompt_for_config(context, initial_config: dict):  # pragma: no cover
    """Prompt user to enter a new config.

    This is copied from
    https://github.com/cookiecutter/cookiecutter/blob/b1f6427606b67362de233588dd7a37496195b031/cookiecutter/prompt.py#L180

    But doesn't prompt for already provided values.
    """
    from cookiecutter.environment import StrictEnvironment
    from cookiecutter.exceptions import UndefinedVariableInTemplate
    from cookiecutter.prompt import prompt_choice_for_config, read_user_dict, read_user_variable, render_variable
    from jinja2.exceptions import UndefinedError

    cookiecutter_dict = OrderedDict(initial_config)
    env = StrictEnvironment(context=context)

    # First pass: Handle simple and raw variables, plus choices.
    # These must be done first because the dictionaries keys and
    # values might refer to them.
    for key, raw in context["cookiecutter"].items():
        if key in cookiecutter_dict:
            continue
        if key.startswith("_") and not key.startswith("__"):
            cookiecutter_dict[key] = raw
            continue
        elif key.startswith("__"):
            cookiecutter_dict[key] = render_variable(env, raw, cookiecutter_dict)
            continue

        try:
            if isinstance(raw, list):
                # We are dealing with a choice variable
                val = prompt_choice_for_config(cookiecutter_dict, env, key, raw, False)
                cookiecutter_dict[key] = val
            elif not isinstance(raw, dict):
                # We are dealing with a regular variable
                val = render_variable(env, raw, cookiecutter_dict)

                val = read_user_variable(key, val)

                cookiecutter_dict[key] = val
        except UndefinedError as err:
            msg = "Unable to render variable '{}'".format(key)
            raise UndefinedVariableInTemplate(msg, err, context)

    # Second pass; handle the dictionaries.
    for key, raw in context["cookiecutter"].items():
        # Skip private type dicts not ot be rendered.
        if key in cookiecutter_dict:
            continue
        if key.startswith("_") and not key.startswith("__"):
            continue

        try:
            if isinstance(raw, dict):
                # We are dealing with a dict variable
                val = render_variable(env, raw, cookiecutter_dict)

                if not key.startswith("__"):
                    val = read_user_dict(key, val)

                cookiecutter_dict[key] = val
        except UndefinedError as err:
            msg = "Unable to render variable '{}'".format(key)
            raise UndefinedVariableInTemplate(msg, err, context)

    return cookiecutter_dict


def _extract_directory_field(template_path: Path) -> str:
    """Extract the name of the cookiecutter context field which controls the directory name."""
    from cookiecutter.find import find_template

    template_dir_name = Path(find_template(str(template_path))).name
    match = re.search(r"(?<=cookiecutter\.)[\w-]+", template_dir_name)
    if not match:
        raise WorkspaceTemplateError(f"Failed extracting context field from {template_dir_name!r}.")
    return match.group()
