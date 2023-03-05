"""
Utilities for managing configuration.
"""

from __future__ import annotations

import os
import re
import sys
import typing as T
import unicodedata
from pathlib import Path

import toml
from jinja2 import Environment, FileSystemLoader, Template

from mapyde import prefix
from mapyde.typing import ImmutableConfig, MutableConfig

# importlib.resources.as_file wasn't added until Python 3.9
# c.f. https://docs.python.org/3.9/library/importlib.html#importlib.resources.as_file
if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources


def merge(
    left: MutableConfig, right: ImmutableConfig, path: list[str] | None = None
) -> ImmutableConfig:
    """
    merges right dictionary into left dictionary
    """
    if path is None:
        path = []
    for key in right:
        if key in left:
            if isinstance(left[key], dict) and isinstance(right[key], dict):
                merge(left[key], right[key], [*path, str(key)])
            else:
                left[key] = right[key]
        else:
            left[key] = right[key]
    return left


def render_string(blob: str, variables: ImmutableConfig | None = None) -> str:
    """
    Render a string using various variables set by the mapyde package.
    """
    variables = variables or {}
    tpl = Template(blob)
    return tpl.render(
        PWD=os.getenv("PWD"),
        USER=os.getenv("USER"),
        MAPYDE_DATA=prefix.data,  # type: ignore[attr-defined]
        MAPYDE_CARDS=prefix.cards,  # type: ignore[attr-defined]  # pylint: disable=no-member
        MAPYDE_LIKELIHOODS=prefix.likelihoods,  # type: ignore[attr-defined]  # pylint: disable=no-member
        MAPYDE_SCRIPTS=prefix.scripts,  # type: ignore[attr-defined]  # pylint: disable=no-member
        MAPYDE_TEMPLATES=prefix.templates,  # type: ignore[attr-defined]  # pylint: disable=no-member
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
    with Path(tpl.filename).open(encoding="utf-8") as fpointer:
        return toml.load(fpointer)


def build_config(user: MutableConfig) -> T.Any:
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
            msg = f"{template_path} does not exist."
            raise OSError(msg)
        defaults = load_config(template.name, str(template.parent))

    variables = merge(defaults, user)
    return toml.loads(render_string(toml.dumps(variables), variables))


def output_path(config: ImmutableConfig) -> Path:
    """
    Return the output path from the config.
    """
    return Path(config["base"]["path"]).joinpath(config["base"]["output"]).resolve()


def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")
