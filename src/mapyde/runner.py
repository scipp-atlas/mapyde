from __future__ import annotations

import typing as T
from pathlib import Path

from mapyde.backends import madgraph
from mapyde.container import Container


def run_madgraph(config: dict[str, T.Any]) -> tuple[bytes, bytes]:
    # ./test/wrapper_mgpy.py config_file
    madgraph.generate_mg5config(config)

    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['madgraph']['version']}"
    command = b"mg5_aMC /data/run.mg5 && rsync -a PROC_madgraph /data/madgraph\n"

    with Container(
        image=image,
        name=f"{config['base']['output']}__mgpy",
        mounts=[
            (str(Path(config["base"]["path"]).joinpath("cards").resolve()), "/cards"),
            (
                str(
                    Path(config["base"]["path"])
                    .joinpath(config["base"]["output"])
                    .resolve()
                ),
                "/data",
            ),
        ],
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_delphes(config: dict[str, T.Any]) -> None:
    # ./test/wrapper_delphes.py config_file
    pass


def run_ana(config: dict[str, T.Any]) -> None:
    # recompute XS, override XS if needed,
    # add XS to config, re-dump config file
    # probably want to move this to wrapper_ana.py script

    # ./test/wrapper_ana.py config_file
    pass


def run_pyhf(config: dict[str, T.Any]) -> None:
    # ./test/wrapper_pyhf.py config_file
    pass
