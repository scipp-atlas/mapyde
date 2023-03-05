"""
Typehint helpers.
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any, Dict, Mapping, Union

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


if TYPE_CHECKING:
    PathOrStr = Union[str, os.PathLike[str]]
    PopenBytes = subprocess.Popen[bytes]
else:
    PathOrStr = Union[str, "os.PathLike[str]"]
    PopenBytes = subprocess.Popen

__all__ = (
    "Literal",
    "PathOrStr",
    "Self",
    "PopenBytes",
)


ImmutableConfig = Mapping[str, Any]
MutableConfig = Dict[str, Any]
