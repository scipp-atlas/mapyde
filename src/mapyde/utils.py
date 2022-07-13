"""
Utilities for managing configuration.
"""

from __future__ import annotations

import os
import sys
import typing as T
from pathlib import Path

import toml
from jinja2 import Environment, FileSystemLoader, Template

from mapyde import cards, data, likelihoods, scripts, templates

# importlib.resources.as_file wasn't added until Python 3.9
# c.f. https://docs.python.org/3.9/library/importlib.html#importlib.resources.as_file
if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources


def merge(
    left: dict[str, T.Any], right: dict[str, T.Any], path: T.Optional[list[str]] = None
) -> dict[str, T.Any]:
    """
    merges right dictionary into left dictionary
    """
    if path is None:
        path = []
    for key in right:
        if key in left:
            if isinstance(left[key], dict) and isinstance(right[key], dict):
                merge(left[key], right[key], path + [str(key)])
            else:
                left[key] = right[key]
        else:
            left[key] = right[key]
    return left


def render_string(blob: str, variables: T.Optional[dict[str, T.Any]] = None) -> str:
    variables = variables or {}
    tpl = Template(blob)
    return tpl.render(
        PWD=os.getenv("PWD"),
        USER=os.getenv("USER"),
        MAPYDE_DATA=data,
        MAPYDE_CARDS=cards,
        MAPYDE_LIKELIHOODS=likelihoods,
        MAPYDE_SCRIPTS=scripts,
        MAPYDE_TEMPLATES=templates,
        **variables,
    )


def env_override(value: T.Any, key: str) -> T.Any:
    """
    Helper function for jinja2 to override environment variables
    """
    return os.getenv(key, value)


def load_config(filename: str, cwd: str = ".") -> T.Any:
    """
    Helper function to load a local toml configuration by filename
    """
    env = Environment(loader=FileSystemLoader(cwd))
    env.filters["env_override"] = env_override

    tpl = env.get_template(filename)
    assert tpl.filename
    return toml.load(open(tpl.filename, encoding="utf-8"))


def build_config(user: dict[str, T.Any]) -> T.Any:
    """
    Function to build a configuration from a user-provided toml configuration on top of the base/template one.
    """

    template_path = Path(
        render_string(
            user["base"].get("template", "{{MAPYDE_TEMPLATES}}/defaults.toml")
        )
    )

    with resources.as_file(template_path) as template:
        if not template.exists():
            raise OSError(f"{template_path} does not exist.")
        defaults = load_config(template.name, str(template.parent))

    variables = merge(defaults, user)
    config = toml.loads(render_string(toml.dumps(variables), variables))

    return config
