"""
File containing functionality for running the various steps in the workflow.
"""
from __future__ import annotations

import sys
from pathlib import Path

from mapyde import utils
from mapyde.backends import madgraph
from mapyde.container import Container
from mapyde.typing import ImmutableConfig, PathOrStr


def mounts(config: ImmutableConfig) -> list[tuple[PathOrStr, PathOrStr]]:
    """
    define mount points for all containers
    """

    return [
        (str(Path(config["base"]["cards_path"]).resolve()), "/cards"),
        (str(Path(config["base"]["scripts_path"]).resolve()), "/scripts"),
        (str(Path(config["base"]["likelihoods_path"]).resolve()), "/likelihoods"),
        (str(utils.output_path(config)), "/data"),
    ]


def run_madgraph(config: ImmutableConfig) -> tuple[bytes, bytes]:
    """
    Run madgraph.
    """

    # in some cases we'll need to run MG once to get a XS, e.g. without decays, and then run again with the "real" proc card.
    if (
        "run_without_decays" in config["madgraph"]
        and config["madgraph"]["run_without_decays"]
    ):

        # modify config to run without decays and store in a separate area
        origcard = config["madgraph"]["proc"]["card"]
        origout = config["base"]["output"]
        origpythia = config["pythia"]["skip"]

        config["madgraph"]["proc"]["card"] = (
            config["madgraph"]["proc"]["card"] + "nodecays"
        )
        config["base"]["output"] = config["base"]["output"] + "nodecays"
        config["pythia"]["skip"] = True

        madgraph.generate_mg5config(config)

        image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['madgraph']['version']}"
        command = bytes(
            f"mg5_aMC /data/{config['madgraph']['generator']['output']} && rsync -a PROC_madgraph /data/madgraph\n",
            "utf-8",
        )

        with Container(
            image=image,
            name=f"{config['base']['output']}__mgpy",
            mounts=mounts(config),
            stdout=sys.stdout,
            output=(utils.output_path(config).joinpath(config["base"]["logs"])),
        ) as container:
            stdout, stderr = container.process.communicate(command)

        # change config options back
        config["madgraph"]["proc"]["card"] = origcard
        config["base"]["output"] = origout
        config["pythia"]["skip"] = origpythia

    madgraph.generate_mg5config(config)

    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['madgraph']['version']}"
    command = bytes(
        f"mg5_aMC /data/{config['madgraph']['generator']['output']} && rsync -a PROC_madgraph /data/madgraph\n",
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__mgpy",
        mounts=mounts(config),
        stdout=sys.stdout,
        output=(utils.output_path(config).joinpath(config["base"]["logs"])),
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_delphes(config: ImmutableConfig) -> tuple[bytes, bytes]:
    """
    Run delphes.
    """
    # ./test/wrapper_delphes.py config_file
    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['delphes']['version']}"
    command = bytes(
        f"""pwd && ls -lavh && ls -lavh /data && cp $(find /data/ -name "*hepmc.gz") hepmc.gz && \
gunzip hepmc.gz && \
/bin/ls -ltrh --color && \
mkdir -p {Path(config['delphes']['output']).parent} && \
/usr/local/share/delphes/delphes/DelphesHepMC2 /cards/delphes/{config['delphes']['card']} {Path(config['delphes']['output'])} hepmc && \
rsync -rav --exclude hepmc . /data/""",
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__delphes",
        mounts=mounts(config),
        stdout=sys.stdout,
        output=(utils.output_path(config).joinpath(config["base"]["logs"])),
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_ana(config: ImmutableConfig) -> tuple[bytes, bytes]:
    """
    Run analysis.
    """
    xsec = 1000.0

    if config["analysis"]["XSoverride"] > 0:
        xsec = config["analysis"]["XSoverride"]
    else:
        if (
            "run_without_decays" in config["madgraph"]
            and config["madgraph"]["run_without_decays"]
        ):
            # modify config to access XS from run without decays
            origcard = config["madgraph"]["proc"]["card"]
            origout = config["base"]["output"]

            config["madgraph"]["proc"]["card"] = (
                config["madgraph"]["proc"]["card"] + "nodecays"
            )
            config["base"]["output"] = config["base"]["output"] + "nodecays"

            with utils.output_path(config).joinpath(
                config["base"]["logs"], "docker_mgpy.log"
            ).open(encoding="utf-8") as fpointer:
                for line in fpointer.readlines():
                    # TODO: can we flip this logic around to be better?
                    # refactor into a parse_xsec utility or something?
                    if config["madgraph"]["run"]["options"]["xqcut"] > 0:
                        if "cross-section :" in line:
                            xsec = float(line.split()[3])  # take the last instance
                    else:
                        if "Cross-section :" in line:
                            xsec = float(line.split()[2])  # take the last instance

            if "branchingratio" in config["analysis"]:
                xsec *= config["analysis"]["branchingratio"]

            # change config options back
            config["madgraph"]["proc"]["card"] = origcard
            config["base"]["output"] = origout
        else:
            with utils.output_path(config).joinpath(
                config["base"]["logs"], "docker_mgpy.log"
            ).open(encoding="utf-8") as fpointer:
                for line in fpointer.readlines():
                    # TODO: can we flip this logic around to be better?
                    # refactor into a parse_xsec utility or something?
                    if config["madgraph"]["run"]["options"]["xqcut"] > 0:
                        if "cross-section :" in line:
                            xsec = float(line.split()[3])  # take the last instance
                    else:
                        if "Cross-section :" in line:
                            xsec = float(line.split()[2])  # take the last instance

    if config["analysis"]["kfactor"] > 0:
        xsec *= config["analysis"]["kfactor"]

    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['delphes']['version']}"
    command = bytes(
        f"""mkdir -p {Path(config['analysis']['output']).parent} && \
/scripts/{config['analysis']['script']} --input {Path('/data').joinpath(config['delphes']['output'])} \
                                        --output {config['analysis']['output']} \
                                        --lumi {config['analysis']['lumi']} \
                                        --XS {xsec} && \
rsync -rav . /data/""",
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__hists",
        mounts=mounts(config),
        stdout=sys.stdout,
        output=(utils.output_path(config).joinpath(config["base"]["logs"])),
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_simpleanalysis(config: ImmutableConfig) -> tuple[bytes, bytes]:
    """
    Run SimpleAnalysis.
    """

    image = "gitlab-registry.cern.ch/atlas-phys-susy-wg/simpleanalysis:master"
    command = bytes(
        f"""simpleAnalysis -a {config['simpleanalysis']['name']} {config['analysis']['output']} -n""",
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__simpleanalysis",
        mounts=mounts(config),
        stdout=sys.stdout,
        cwd="/data",
        output=(utils.output_path(config).joinpath(config["base"]["logs"])),
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_sa2json(config: ImmutableConfig) -> tuple[bytes, bytes]:
    """
    Convert SA ROOT file to HiFa JSON.
    """
    assert config

    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['sa2json']['image']}"
    command = bytes(
        f"""python /scripts/SAtoJSON.py -i {config['simpleanalysis']['name']}.root -o {config['sa2json']['output']} -n {config['base']['output']} -b /likelihoods/{config['pyhf']['likelihood']} -l {config['analysis']['lumi']}""",
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__SA2json",
        mounts=mounts(config),
        stdout=sys.stdout,
        output=(utils.output_path(config).joinpath(config["base"]["logs"])),
        cwd="/data",
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_pyhf(config: ImmutableConfig) -> tuple[bytes, bytes]:
    """
    Run statistical inference via pyhf.
    """
    assert config

    image = f"ghcr.io/scipp-atlas/mario-mapyde/{config['pyhf']['image']}"
    command = bytes(
        f"""time python3.8 /scripts/muscan.py -b /likelihoods/{config['pyhf']['likelihood']} -s {config['sa2json']['output']} -n {config['base']['output']} {config['pyhf']['gpu-options']}""",
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__muscan",
        mounts=mounts(config),
        stdout=sys.stdout,
        output=(utils.output_path(config).joinpath(config["base"]["logs"])),
        cwd="/data",
        additional_options=["--gpus", "all"],
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_sherpa(config: ImmutableConfig) -> tuple[bytes, bytes]:
    """
    Run sherpa.
    """

    output_path = (
        Path(config["base"]["path"]).joinpath(config["base"]["output"]).resolve()
    )
    output_path.mkdir(parents=True, exist_ok=True)

    image = "sherpamc/sherpa:2.2.7"
    command = bytes(
        f"""/bin/bash -c "mkdir sherpa && \
cd sherpa && \
cp -p /cards/sherpa/{config['sherpa']['proc']} . && \
ls -ltrh && \
cat {config['sherpa']['proc']} && \
mpirun -n {config['sherpa']['cores']} Sherpa -f {config['sherpa']['proc']} -e {config['sherpa']['nevents']} && \
mv sherpa.hepmc.hepmc2g sherpa.hepmc.gz && \
cd ../ && \
cp -a sherpa/ /data/" """,
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__sherpa",
        mounts=mounts(config),
        stdout=sys.stdout,
        output=(utils.output_path(config).joinpath(config["base"]["logs"])),
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr


def run_root2hdf5(config: ImmutableConfig) -> tuple[bytes, bytes]:
    """
    Transform ROOT file to hdf5 format
    """
    assert config

    image = "ghcr.io/scipp-atlas/mario-mapyde/pyplotting:latest"
    command = bytes(
        f"""python3 /scripts/root2hdf5.py {config['root2hdf5']['input']}:{config['root2hdf5']['treename']} """,
        "utf-8",
    )

    with Container(
        image=image,
        name=f"{config['base']['output']}__root2hdf5",
        mounts=mounts(config),
        stdout=sys.stdout,
        output=(utils.output_path(config).joinpath(config["base"]["logs"])),
        cwd="/data",
    ) as container:
        stdout, stderr = container.process.communicate(command)

    return stdout, stderr
