"""
Typehint helpers.
"""
from __future__ import annotations

import os
import subprocess
import sys
import typing as T

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

__all__ = (
    "Literal",
    "PathOrStr",
    "PopenBytes",
)

if T.TYPE_CHECKING:
    PathOrStr = T.Union[str, os.PathLike[str]]
    PopenBytes = subprocess.Popen[bytes]
else:
    PathOrStr = T.Union[str, "os.PathLike[str]"]
    PopenBytes = subprocess.Popen

ImmutableConfig = T.Mapping[str, T.Any]
MutableConfig = T.Dict[str, T.Any]
