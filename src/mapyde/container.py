"""
Core Container functionality for managing OCI images.
"""
from __future__ import annotations

import os
import subprocess
import typing as T
import uuid
from pathlib import Path
from types import TracebackType

from mapyde.typing import Literal, PathOrStr, PopenBytes

ContainerEngine = Literal["docker"]  # add support for podman later


class Container:
    """
    An object that represents a running OCI container.
    """

    process: PopenBytes
    stdin: T.IO[bytes]
    stdout: T.Optional[T.Union[T.IO[bytes], T.IO[str]]]

    def __init__(
        self,
        *,
        image: str,
        user: T.Optional[int] = None,
        group: T.Optional[int] = None,
        mounts: T.Optional[list[tuple[PathOrStr, PathOrStr]]] = None,
        cwd: T.Optional[PathOrStr] = "/tmp",
        engine: ContainerEngine = "docker",
        name: T.Optional[str] = None,
        stdout: T.Optional[T.Union[T.IO[bytes], T.IO[str]]] = None,
        output: T.Optional[Path] = None,
        additional_options: T.Optional[list[str]] = None,
    ):
        if not image:
            raise ValueError("Must specify an image to run.")

        self.image = image
        self.user = user or os.geteuid()
        self.group = group or os.getegid()
        self.mounts = mounts or []
        self.cwd = cwd
        self.engine = engine
        self.name = name
        self.stdin_config = subprocess.PIPE
        self.stdout_config = stdout or subprocess.PIPE
        self.stderr_config = subprocess.STDOUT
        self.output = output
        self.additional_options = additional_options or []

    def __enter__(self) -> Container:
        self.name = self.name or f"mario-mapyde-{uuid.uuid4()}"

        subprocess.run(
            [
                self.engine,
                "create",
                f"--name={self.name}",
                "--interactive",
                f"--user={self.user}:{self.group}",
                *[f"--volume={local}:{host}" for local, host in self.mounts],
                f"--workdir={self.cwd}",
                *self.additional_options,
                self.image,
            ],
            check=True,
        )

        self.process = subprocess.Popen(
            [
                self.engine,
                "start",
                "--attach",
                "--interactive",
                self.name,
            ],
            stdin=self.stdin_config,
            stdout=self.stdout_config,
        )

        assert self.process.stdin
        self.stdin = self.process.stdin
        self.stdout = self.process.stdout

        return self

    def __exit__(
        self,
        exc_type: T.Optional[T.Type[BaseException]],
        exc_val: T.Optional[BaseException],
        exc_tb: T.Optional[TracebackType],
    ) -> None:

        if self.output:
            # dump log files
            assert self.name
            logfiletag = self.name[self.name.rfind("__") + 2 :]
            self.output.mkdir(parents=True, exist_ok=True)
            with self.output.joinpath(f"docker_{logfiletag}.log").open(
                "w", encoding="utf-8"
            ) as logfile:
                subprocess.run(
                    [
                        self.engine,
                        "logs",
                        self.name,
                    ],
                    stdout=logfile,
                    stderr=logfile,
                    check=False,
                )

        if not self.stdin.closed:
            self.stdin.write(b"exit 0\n")
            self.stdin.flush()
            self.process.wait(timeout=30)
            self.stdin.close()

        if self.stdout and not self.stdout.closed:
            self.stdout.close()

        assert isinstance(self.name, str)

        subprocess.run(
            [self.engine, "rm", "--force", "-v", self.name],
            stdout=subprocess.DEVNULL,
            check=False,
        )

        self.name = None
