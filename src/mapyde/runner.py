from __future__ import annotations

import typing as T
from pathlib import Path

from maypde.container import Container

from mapyde.backends import madgraph


def run_madgraph(config: dict[str, T.Any]) -> None:
    # ./test/wrapper_mgpy.py config_file
    madgraph.generate_mg5config(config)

    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['madgraph']['version']}"
    command = "mg5_aMC /data/run.mg5 && rsync -a PROC_madgraph /data/madgraph"

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
        container.process.run(command)
        print(container.stdout.read())


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
