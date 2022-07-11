from __future__ import annotations

import os
import subprocess
import typing as T

if T.TYPE_CHECKING:
    PathOrStr = T.Union[str, os.PathLike[str]]
    PopenBytes = subprocess.Popen[bytes]
else:
    PathOrStr = T.Union[str, "os.PathLike[str]"]
    PopenBytes = subprocess.Popen
