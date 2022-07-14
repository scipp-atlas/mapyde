"""
Copyright (c) 2022 Michael Hance and Giordon Stark. All rights reserved.

mario-mapyde: A great package.
"""


from __future__ import annotations

import sysconfig
from pathlib import Path

from mapyde._version import __version__

data = Path(sysconfig.get_path("data")).joinpath("share", __name__)
cards = data / "cards"
likelihoods = data / "likelihoods"
scripts = data / "scripts"
templates = data / "templates"

__all__ = ("__version__", "data", "cards", "likelihoods", "scripts", "templates")
