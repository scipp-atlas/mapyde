from __future__ import annotations

import os
import typing as T

import toml
from jinja2 import Environment, FileSystemLoader, Template


def merge(
    a: dict[str, T.Any], b: dict[str, T.Any], path: T.Optional[list[str]] = None
) -> dict[str, T.Any]:
    "merges b into a"
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def env_override(value: T.Any, key: str) -> T.Any:
    return os.getenv(key, value)


def load_config(filename: str, cwd: str = ".") -> T.Any:
    env = Environment(loader=FileSystemLoader(cwd))
    env.filters["env_override"] = env_override

    tpl = env.get_template(filename)
    return toml.load(open(tpl.filename))


def build_config(user: dict[str, T.Any]) -> T.Any:
    defaults = load_config("defaults.toml", "./templates")

    variables = merge(defaults, user)
    tpl = Template(toml.dumps(variables))
    config = toml.loads(
        tpl.render(PWD=os.getenv("PWD"), USER=os.getenv("USER"), **variables)
    )

    return config
