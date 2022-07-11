from __future__ import annotations

import subprocess
import typing as T
import uuid
from types import TracebackType

from typing_extensions import Literal

from mapyde.typing import PathOrStr, PopenBytes

ContainerEngine = Literal["docker"]  # add support for podman later


class Container:
    """
    An object that represents a running OCI container.
    """

    process: PopenBytes
    stdin: T.IO[bytes]
    stdout: T.IO[bytes]

    def __init__(
        self,
        *,
        image: str,
        cwd: T.Optional[PathOrStr],
        engine: ContainerEngine = "docker",
        name: T.Optional[str] = None,
    ):
        if not image:
            raise ValueError("Must specify an image to run.")

        self.image = image
        self.cwd = cwd
        self.name = name
        self.engine = engine

    def __enter__(self) -> Container:
        self.name = f"mario-mapyde-{uuid.uuid4()}"

        subprocess.run(
            [
                self.engine,
                "create",
                f"--name={self.name}",
                "--interactive",
                "--volume=/:/host",
                self.image,
            ],
            check=True,
        )

        self.process = subprocess.Popen(
            [self.engine, "start", "--attach", "--interactive", self.name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        assert self.process.stdin and self.process.stdout
        self.stdin = self.process.stdin
        self.stdout = self.process.stdout

        return self

    def __exit__(
        self,
        exc_type: T.Optional[T.Type[BaseException]],
        exc_val: T.Optional[BaseException],
        exc_tb: T.Optional[TracebackType],
    ) -> None:
        self.stdin.write(b"exit 0\n")
        self.stdin.flush()
        self.process.wait(timeout=30)
        self.stdin.close()
        self.stdout.close()

        assert isinstance(self.name, str)

        subprocess.run(
            [self.engine, "rm", "--force", "-v", self.name],
            stdout=subprocess.DEVNULL,
            check=False,
        )

        self.name = None
