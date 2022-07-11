from __future__ import annotations

import os
import typing as T

import toml
from jinja2 import Environment, FileSystemLoader, Template


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def merge(a: dict, b: dict, path: list = None) -> dict:
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


def load_config(filename: str, cwd: str = ".") -> dict:
    env = Environment(loader=FileSystemLoader(cwd))
    env.filters["env_override"] = env_override

    tpl = env.get_template(filename)
    return toml.load(open(tpl.filename))


def build_config(user: dict) -> dict:
    defaults = load_config("defaults.toml", "./templates")

    variables = merge(defaults, user)
    tpl = Template(toml.dumps(variables))
    config = toml.loads(
        tpl.render(PWD=os.getenv("PWD"), USER=os.getenv("USER"), **variables)
    )

    return dotdict(config)
