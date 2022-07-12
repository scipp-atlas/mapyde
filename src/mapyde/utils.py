"""
Utilities for managing configuration.
"""

from __future__ import annotations

import os
import typing as T

import toml
from jinja2 import Environment, FileSystemLoader, Template


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
    defaults = load_config("defaults.toml", "./templates")

    variables = merge(defaults, user)
    tpl = Template(toml.dumps(variables))
    config = toml.loads(
        tpl.render(PWD=os.getenv("PWD"), USER=os.getenv("USER"), **variables)
    )

    return config
