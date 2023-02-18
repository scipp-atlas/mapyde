"""
Copyright (c) 2022 Michael Hance and Giordon Stark. All rights reserved.

mapyde: A great package.
"""


from __future__ import annotations

import sysconfig
from pathlib import Path

from mapyde._version import __version__

for scheme_name in sysconfig.get_scheme_names()[
    ::-1
]:  # ('posix_user', 'posix_prefix', 'posix_home', 'osx_framework_user', 'nt_user', 'nt')
    data = Path(sysconfig.get_path("data", scheme_name)).joinpath("share", __name__)
    if data.exists():
        break

cards = data / "cards"
likelihoods = data / "likelihoods"
scripts = data / "scripts"
templates = data / "templates"

__all__ = ("__version__", "data", "cards", "likelihoods", "scripts", "templates")
