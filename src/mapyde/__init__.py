"""
Copyright (c) 2022 Michael Hance and Giordon Stark. All rights reserved.

mapyde: A great package.
"""


from __future__ import annotations

import sysconfig
from pathlib import Path

from mapyde import prefix
from mapyde._version import __version__

for scheme_name in sysconfig.get_scheme_names()[
    ::-1
]:  # ('posix_user', 'posix_prefix', 'posix_home', 'osx_framework_user', 'nt_user', 'nt')
    prefix.data = Path(sysconfig.get_path("data", scheme_name)).joinpath(  # type: ignore[attr-defined]
        "share", __name__
    )
    if prefix.data.exists():  # type: ignore[attr-defined]
        break

__all__ = ("__version__", "prefix")
