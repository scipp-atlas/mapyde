"""
Helpers for madgraph
"""

from __future__ import annotations

import logging
import multiprocessing
import re
import shutil
import sys
from pathlib import Path

import in_place
from jinja2 import StrictUndefined, Template

from mapyde.typing import ImmutableConfig
from mapyde.utils import render_string

logging.basicConfig()
log = logging.getLogger()


def generate_proc_card(config: ImmutableConfig, output_path: Path) -> Path:
    """
    Helper for creating the madgraph process card through two options:

      - specifying the path inside process_path for the card to copy over
      - specifying the contents as part of the config to use to make the process card

    Examples:

    ``` toml title="user_existing-card.toml"
    [madgraph.proc]
    name = "isrslep"
    card = "{{madgraph['proc']['name']}}"
    contents = false # (1)!
    ```

    1. specifying `false` (default) for the `contents` option while including the
    path to the card is the way to copy the card `isrslep` from the process
    card directory that is configured.

    ``` toml title="user_on-the-fly.toml"
    [madgraph.proc]
    name = "isrslep"
    card = false
    contents = \"\"\"\\
    import model MSSM_SLHA2
    define lep = e- e+ mu- mu+ ta- ta+
    generate p p > z, z > lep lep
    output -f
    \"\"\" # (1)!
    ```

    1. specifying the full process card contents to use for the process card will
    generate a process card with the specified name instead of copying over
    `isrslep` from the process card directory.
    """

    assert bool(config["madgraph"]["proc"]["card"]) ^ bool(
        config["madgraph"]["proc"]["contents"]
    ), "Must specify either the Madgraph process card to copy or the contents to use to generate a Madgraph process card."

    if config["madgraph"]["proc"]["contents"]:
        new_proc_card_path = output_path.joinpath(config["madgraph"]["proc"]["name"])
        new_proc_card_path.write_text(config["madgraph"]["proc"]["contents"])
    else:
        # Copy the proc card
        proc_card_path = (
            Path(config["base"]["process_path"])
            .joinpath(config["madgraph"]["proc"]["card"])
            .resolve()
        )
        new_proc_card_path = output_path.joinpath(proc_card_path.name)
        shutil.copyfile(proc_card_path, new_proc_card_path)

    log.info("Process Card: %s", new_proc_card_path)
    return new_proc_card_path


def generate_mg5commands(config: ImmutableConfig) -> None:
    """
    Helper for generating the madgraph configs. Replaces mg5creator.py.
    """
    old_versions = ["2.4.3", "2.3.3"]
    is_old_version = False
    if any(version in config["madgraph"]["version"] for version in old_versions):
        is_old_version = True
        log.warning("Old madgraph version detected: %s", config["madgraph"]["version"])

    output_path = (
        Path(config["base"]["path"]).joinpath(config["base"]["output"]).resolve()
    )
    output_path.mkdir(parents=True, exist_ok=True)

    # Ensure pythia card exists
    _pythia_card_path = Path(config["base"]["pythia_path"]).joinpath(
        config["pythia"]["card"]
    )
    if not _pythia_card_path.exists():
        log.error("%s does not exist.", _pythia_card_path)
        sys.exit(1)

    # Controls whether to run Pythia8 or not
    # pylint: disable-next=possibly-unused-variable
    pythia_config_path = ""
    if not config["pythia"]["skip"]:
        # Copy the pythia card
        pythia_card_path = (
            Path(config["base"]["pythia_path"])
            .joinpath(config["pythia"]["card"])
            .resolve()
        )
        new_pythia_card_path = output_path.joinpath("pythia_card.dat")

        # block below replaces a straightforward copy of pythia card to run area
        with new_pythia_card_path.open("w", encoding="utf-8") as new_pythia_card:
            with pythia_card_path.open(encoding="utf-8") as pcard:
                for line in pcard:
                    # now handle specific pythia options.  can be refactored later to be more elegant.
                    # really only turning MPI on/off at the moment
                    if "partonlevel:mpi" in line and "mpi" in config["pythia"]:
                        if config["pythia"]["mpi"] == "on":
                            new_pythia_card.write("partonlevel:mpi = on")
                        elif config["pythia"]["mpi"] == "off":
                            new_pythia_card.write("partonlevel:mpi = off")
                        else:
                            log.error(
                                "partonlevel:mpi can only be 'on' or 'off', not %s",
                                config["pythia"]["mpi"],
                            )
                            sys.exit(1)
                    else:
                        new_pythia_card.write(line)

            if "additional_opts" in config["pythia"]:
                new_pythia_card.write("\n")
                new_pythia_card.write(config["pythia"]["additional_opts"])

        log.info("Pythia Card: %s", new_pythia_card_path)
        pythia_config_path = f"/data/{new_pythia_card_path.name}"

    substitution = {
        "ecms": float(config["madgraph"]["run"]["ecms"]) / 2,
        "nevents": int(config["madgraph"]["run"]["nevents"]),
        "iseed": int(config["madgraph"]["run"]["seed"]),
    }

    masses = config["madgraph"].get("masses", {})
    if any(key in masses for key in substitution):
        msg = "Particles cannot be named ecms, nevents, or iseed."
        raise ValueError(msg)

    # Update the param card
    param_card_path = (
        Path(config["base"]["param_path"])
        .joinpath(config["madgraph"]["paramcard"])
        .resolve()
    )
    new_param_card_path = output_path.joinpath(param_card_path.name)
    log.info("Param Card: %s", new_param_card_path)

    # mass substitutions can be either of the form:
    #
    # > MSLEP = 100
    #
    # where "MSLEP" is a placeholder mass string inside the param card that must be replaced with a number before running madgraph, or
    #
    # > 1000011 = 100
    #
    # where 1000011 is the PDG ID of the particle that can already have a placeholder mass that we want to replace with the value specified in the toml file.
    #
    # the two different types of substitutions need to be handled differently.

    param_card_read_text = param_card_path.read_text(encoding="utf-8")

    # do the second kind of substitution
    masses_to_remove = []
    for pdgid, mass in masses.items():
        # avoid dealing with the templated replacement syntax here
        try:
            int(pdgid)  # force an exception for entries like "MSLEP = 100"

            # figure out where the mass block is, so we only modify things in there
            blockmassbegin = param_card_read_text.find("Block mass")
            blockmassend = param_card_read_text.find("Block", blockmassbegin + 1)

            # figure out where this specific particle is, within the block
            pdgidloc = param_card_read_text.find(
                " " + pdgid, blockmassbegin, blockmassend
            )
            pdgidloclineend = param_card_read_text.find("\n", pdgidloc)

            # now rebuild the param card around the new mass
            param_card_read_text = (
                param_card_read_text[: pdgidloc + len(pdgid) + 2]
                + "   "
                + str(mass)
                + param_card_read_text[pdgidloclineend:]
            )

            # note that we've already processed this mass so we can avoid doing it again later
            masses_to_remove.append(pdgid)
        # pylint: disable-next=bare-except
        except:  # noqa: E722
            # should throw a "ValueError", but I can't predict all the silly ways
            # people may do templated substitution....
            pass

    # don't try to update masses that have already been dealt with above.
    for pdgid in masses_to_remove:
        masses.pop(pdgid)

    # now do the first kind of substitution
    substitution.update(masses)

    log.info("The following values will be substituted in where possible:")
    for key, value in substitution.items():
        log.info("    $%s = %s", key, value)

    new_param_card_path.write_text(
        Template(param_card_read_text, undefined=StrictUndefined).render(substitution),
        encoding="utf-8",
    )

    # Update the run card
    run_card_path = (
        Path(config["base"]["run_path"])
        .joinpath(config["madgraph"]["run"]["card"])
        .resolve()
    )
    if is_old_version:
        log.warning("Changing the run card due to old madgraph version.")
        run_card_path = run_card_path.parent.joinpath("default_LO_oldformat.dat")
    new_run_card_path = output_path.joinpath(run_card_path.name)
    log.info("Run Card: %s", new_run_card_path)

    # -- first do global opts
    new_run_card_path.write_text(
        Template(
            run_card_path.read_text(encoding="utf-8"), undefined=StrictUndefined
        ).render(substitution),
        encoding="utf-8",
    )

    # -- now specific opts.  may want to reverse this order at some point, and do the specific before global.
    # Note: this will only work with options in the run card that contain a "!" in the line, indicating a comment at the end of the line.
    run_options = {**config["madgraph"]["run"].get("options", {})}

    # env = Environment()
    # parsed_content = env.parse('my text here')
    # tpl_variables = meta.find_undeclared_variables(parsed)

    pattern = re.compile(
        r"^\s*(?P<value>[^\s]+)\s*=\s*(?P<key>[a-z_0-9]+)\s*\!.*$", re.DOTALL
    )
    with in_place.InPlace(new_run_card_path) as fpointer:
        for line in fpointer:
            output = line
            match = pattern.match(line)
            if match:
                groups = match.groupdict()
                span = match.span("value")
                newvalue = str(run_options.pop(groups["key"], groups["value"]))
                # update the line based on input from the user, default to what is in the file
                output = line[: span[0]] + newvalue + line[span[1] :]
                if newvalue != groups["value"]:
                    log.info(
                        "    replacing value for %s: %s -> %s",
                        groups["key"],
                        groups["value"],
                        newvalue,
                    )
            fpointer.write(output)

    unused_keys = list(run_options.keys())
    if unused_keys:
        log.error("Unused keys supplied by you: %s", unused_keys)
        raise KeyError(unused_keys[0])

    new_proc_card_path = generate_proc_card(config, output_path)

    # Create the madgraph configuration card
    mgcommands_card_path = output_path.joinpath(
        config["madgraph"]["commands"]["output"]
    )
    log.info("MadGraph Config: %s", mgcommands_card_path)

    # pylint: disable-next=possibly-unused-variable
    run_mode = ""
    # Figure out the run_mode.  0=single core, 1=cluster, 2=multicore.
    if config["madgraph"]["batch"]:
        run_mode = "set run_mode 0"  # we don't have MadGraph launch cluster jobs for us, we handle that ourselves.
    elif int(config["madgraph"]["cores"]) > 0:
        run_mode = f"set run_mode 2\nset nb_core {config['madgraph']['cores']}"
    else:
        run_mode = f"set run_mode 2\nset nb_core {multiprocessing.cpu_count() / 2}"

    # figure out if running with madspin or not, and if so, put the card in the right place
    # pylint: disable-next=possibly-unused-variable
    madspin_config_path = ""
    if not config["madspin"]["skip"]:
        # Copy the madspin card
        madspin_card_path = (
            Path(config["base"]["madspin_path"])
            .joinpath(config["madspin"]["card"])
            .resolve()
        )
        new_madspin_card_path = output_path.joinpath("madspin_card.dat")

        # block below replaces a straightforward copy of madspin card to run area,
        # but allows us to modify the card according to config options
        with new_madspin_card_path.open(
            "w", encoding="utf-8"
        ) as new_madspin_card, madspin_card_path.open(encoding="utf-8") as pcard:
            for line in pcard:
                # now handle specific madspin options.  can be refactored later
                # to be more elegant. really only changing the spinmode at the moment
                if "set spinmode" in line and "spinmode" in config["madspin"]:
                    new_madspin_card.write(
                        f"set spinmode {config['madspin']['spinmode']} \n"
                    )
                else:
                    new_madspin_card.write(line)

        log.info("MadSpin Card: %s", new_madspin_card_path)
        madspin_config_path = f"/data/{new_madspin_card_path.name}"

    mg5commands = config["madgraph"]["commands"]["contents"]
    if is_old_version:
        mg5commands = "\n".join(
            line
            for line in mg5commands.splitlines()
            if not line.startswith("set iseed")
            and not line.startswith("shower=")
            and not line.startswith("{pythia_config_path}")
        )

    mg5commands_parsed = render_string(
        mg5commands,
        {
            "run_mode": run_mode,
            "pythia_config_path": pythia_config_path,
            "madspin_config_path": madspin_config_path,
            **config,
        },
    )

    with mgcommands_card_path.open(mode="w", encoding="utf-8") as fpointer:
        # pylint: disable-next=consider-using-with
        with new_proc_card_path.open(encoding="utf-8") as proc_lines:
            for proc_line in proc_lines:
                if not proc_line.strip():
                    continue
                if proc_line.startswith("output"):
                    fpointer.write("output PROC_madgraph\n")
                else:
                    fpointer.write(proc_line)
        fpointer.write(mg5commands_parsed)
