"""
Core Container functionality for managing OCI images.
"""
from __future__ import annotations

import logging
import os
import shlex
import subprocess
import typing as T
import uuid
from pathlib import Path
from types import TracebackType

from mapyde.typing import Literal, PathOrStr, PopenBytes
from mapyde.utils import slugify

ContainerEngine = Literal[
    "docker", "singularity", "apptainer"
]  # add support for podman later

log = logging.getLogger(__name__)


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
        output_path: T.Optional[Path] = None,
        logs_path: T.Optional[PathOrStr] = None,
        additional_options: T.Optional[list[str]] = None,
    ):
        if not image:
            raise ValueError("Must specify an image to run.")

        try:
            subprocess.run(["bash", "-c", f"hash {engine}"], check=True)
        except subprocess.CalledProcessError as err:
            raise OSError(f"{engine} does not exist on your system.") from err

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
        self.output_path = (output_path or Path()).resolve()
        self.logs_path = logs_path
        self.additional_options = additional_options or []

        self.output_path.mkdir(parents=True, exist_ok=True)
        for host, container in self.mounts:
            if not Path(container).is_absolute():
                raise ValueError(
                    f"The mount {host}:{container} does not point to an absolute path in the container."
                )

    def __enter__(self) -> Container:

        if self.engine in ["singularity", "apptainer"]:
            self.name = self.name or slugify(self.image)

            sif_path = self.output_path.joinpath(f"{self.name}.sif")
            if not sif_path.exists():
                subprocess.run(
                    [
                        self.engine,
                        "build",
                        "--force",
                        "--sandbox",
                        sif_path,
                        f"docker://{self.image}",
                    ],
                    check=True,
                )

                subprocess.run(
                    [
                        "mkdir",
                        *[
                            sif_path.joinpath(Path(container).relative_to("/"))
                            for _, container in self.mounts
                        ],
                    ],
                    check=True,
                )

            else:
                log.warning("%s already exists. Re-using it.", sif_path)

            self.process = subprocess.Popen(
                [
                    self.engine,
                    "shell",
                    *[f"--bind={host}:{container}" for host, container in self.mounts],
                    f"--pwd={self.cwd}",
                    "--no-home",
                    "--cleanenv",
                    "--writable",
                    *self.additional_options,
                    sif_path,
                ],
                stdin=self.stdin_config,
                stdout=self.stdout_config,
            )

        else:
            self.name = self.name or f"mario-mapyde-{uuid.uuid4()}"

            subprocess.run(
                [
                    self.engine,
                    "create",
                    f"--name={self.name}",
                    "--interactive",
                    f"--user={self.user}:{self.group}",
                    *[
                        f"--volume={host}:{container}"
                        for host, container in self.mounts
                    ],
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

        if self.logs_path:
            # dump log files
            assert self.name
            logfiletag = self.name[self.name.rfind("__") + 2 :]

            output = self.output_path.joinpath(self.logs_path).joinpath(
                f"docker_{logfiletag}.log"
            )
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("w", encoding="utf-8") as logfile:
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

        # singularity and apptainer do not have daemons
        if self.engine not in ["singularity", "apptainer"]:
            subprocess.run(
                [self.engine, "rm", "--force", "-v", self.name],
                stdout=subprocess.DEVNULL,
                check=False,
            )

        self.name = None

    def call(
        self,
        args: bytes,
        cwd: PathOrStr | None = None,
        env: dict[str, str] | None = None,
    ) -> tuple[bytes, bytes]:
        """
        Execute the provided command in the container. A smarter version of Container.process.communicate(args).

        Optionally change the current working directory (cwd) and set some environment variables.
        """
        if cwd is None:
            cwd = self.cwd

        chdir = ""
        if cwd:
            # singularity/apptainer mount host $TMPDIR into /tmp which might be
            # unexpectedly full of files so make an empty temporary directory
            chdir = "cd $(mktemp -d)" if cwd == "/tmp" else f"cd {cwd}"

        env_assignments = (
            " ".join(f"{shlex.quote(k)}={shlex.quote(v)}" for k, v in env.items())
            if env is not None
            else ""
        )

        command = bytes(
            f"""{chdir}
                env {env_assignments} {args.decode()}
                """,
            "utf-8",
        )

        return self.process.communicate(command)
