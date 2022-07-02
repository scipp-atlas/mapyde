from __future__ import annotations
import typing as T

from mapyde.backends import madgraph
import os

import docker

client = docker.from_env()


def run_madgraph(config: dict):
    # ./test/wrapper_mgpy.py config_file
    madgraph.generate_mg5config(config)

    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config.madgraph['version']}"
    command = "mg5_aMC /data/run.mg5 && rsync -a PROC_madgraph /data/madgraph"
    options = {
        "name": f"{config.base['output']}__mgpy",
        "remove": True,
        "user": os.geteuid(),
        "group_add": [os.getegid()],
        "mounts": [
            docker.types.Mount(Path(config.base['path']).joinpath("cards"), "/cards"),
            docker.types.Mount(
                Path(config.base['path']).joinpath(config.base['output']), "/data"
            ),
        ],
        "working_dir": "/tmp",
    }

    client.containers.run(image, command, options)


def run_delphes(config: dict):
    # ./test/wrapper_delphes.py config_file
    pass


def run_ana(config: dict):
    # recompute XS, override XS if needed,
    # add XS to config, re-dump config file
    # probably want to move this to wrapper_ana.py script

    # ./test/wrapper_ana.py config_file
    pass


def run_pyhf(config: dict):
    # ./test/wrapper_pyhf.py config_file
    pass
