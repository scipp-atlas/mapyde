"""
File containing functionality for running the various steps in the workflow.
"""
from __future__ import annotations

import sys
import typing as T
from pathlib import Path

from mapyde.backends import madgraph
from mapyde.container import Container


def run_madgraph(config: dict[str, T.Any]) -> tuple[bytes, bytes]:
    """
    Run madgraph.
    """
    # ./test/wrapper_mgpy.py config_file
    madgraph.generate_mg5config(config)

    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['madgraph']['version']}"
    command = b"mg5_aMC /data/run.mg5 && rsync -a PROC_madgraph /data/madgraph\n"

    with Container(
        image=image,
        name=f"{config['base']['output']}__mgpy",
        mounts=[
            (str(Path(config["base"]["cards_path"]).resolve()), "/cards"),
            (
                str(
                    Path(config["base"]["path"])
                    .joinpath(config["base"]["output"])
                    .resolve()
                ),
                "/data",
            ),
        ],
        stdout=sys.stdout,
        output=str(
                    Path(config["base"]["path"])
                    .joinpath(config["base"]["output"])
                    .resolve()
                )
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_delphes(config: dict[str, T.Any]) -> tuple[bytes, bytes]:
    """
    Run delphes.
    """
    # ./test/wrapper_delphes.py config_file
    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['delphes']['version']}"
    command = bytes(
        f"""pwd && ls -lavh && ls -lavh /data && cp $(find /data/ -name "*hepmc.gz") hepmc.gz && \
gunzip hepmc.gz && \
/bin/ls -ltrh --color && \
/usr/local/share/delphes/delphes/DelphesHepMC2 /cards/delphes/{config['delphes']['card']} delphes.root hepmc && \
rsync -rav --exclude hepmc . /data/delphes""",
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__delphes",
        mounts=[
            (str(Path(config["base"]["cards_path"]).resolve()), "/cards"),
            (
                str(
                    Path(config["base"]["path"])
                    .joinpath(config["base"]["output"])
                    .resolve()
                ),
                "/data",
            ),
        ],
        stdout=sys.stdout,
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_ana(config: dict[str, T.Any]) -> tuple[bytes, bytes]:
    """
    Run analysis.
    """
    # ./test/wrapper_delphes.py config_file
    # recompute XS, override XS if needed,
    # add XS to config, re-dump config file
    # probably want to move this to wrapper_ana.py script

    xsec = 10  # TODO

    print(config['analysis']['XSoverride'])
    
    if config['analysis']['XSoverride']>0:
        xsec=config['analysis']['XSoverride']
    else:
        print(str(Path(config["base"]["database"]).resolve()))
        logfile=str(Path(config["base"]["database"]).joinpath(config["base"]["output"]).resolve())
        print(logfile)
        #with open(f"{}/{}/docker_mgpy.log"
        """
        XS=$(grep "Cross-section :" ${database}/${tag}/docker_mgpy.log | tail -1 | awk '{print $8}')
        # if we're doing matching, then take a different value
        if [[ $xqcut != -1 ]]; then
            XS=$(grep "cross-section :" ${database}/${tag}/docker_mgpy.log | tail -1 | awk '{print $9}')
        fi

        if [[ $kfactor != -1 ]]; then
            origXS=$(grep "Cross-section" ${database}/${tag}/docker_mgpy.log | tail -1 | awk '{print $8}')
            XSoverride=$(python3 -c "print(${kfactor}*${origXS})") # k-factor * LO XS
            echo "Changing cross section from $origXS to $XSoverride to account for k-factors"
        fi
        """

    print("heyo")
    return None,None
    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['delphes']['version']}"
    command = bytes(
        f"""/scripts/{config['analysis']['script']} --input /data/delphes/delphes.root --output {config['analysis']['output']} --lumi {config['analysis']['lumi']} --XS {xsec} && rsync -rav . /data/analysis""",
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__hists",
        mounts=[
            (str(Path(config["base"]["cards_path"]).resolve()), "/cards"),
            (
                str(Path(config["base"]["scripts_path"]).resolve()),
                "/scripts",
            ),
            (
                str(
                    Path(config["base"]["path"])
                    .joinpath(config["base"]["output"])
                    .resolve()
                ),
                "/data",
            ),
        ],
        stdout=sys.stdout,
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_pyhf(config: dict[str, T.Any]) -> None:
    """
    Run statistical inference via pyhf.
    """
    # ./test/wrapper_pyhf.py config_file
    assert config
