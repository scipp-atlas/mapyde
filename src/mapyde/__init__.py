"""
Copyright (c) 2022 Michael Hance and Giordon Stark. All rights reserved.

mario-mapyde: A great package.
"""


from __future__ import annotations

import sys

from mapyde._version import __version__

# importlib.resources.as_file wasn't added until Python 3.9
# c.f. https://docs.python.org/3.9/library/importlib.html#importlib.resources.as_file
if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources

data = resources.files("mapyde") / "data"
cards = data / "cards"
templates = data / "templates"

__all__ = ("__version__", "data", "cards", "templates")
