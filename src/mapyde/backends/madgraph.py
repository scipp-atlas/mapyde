import shutil
from string import Template
from pathlib import Path
import pprint
import in_place
import re
import logging
import multiprocessing
import sys

logging.basicConfig()
log = logging.getLogger()


def generate_mg5config(config):
    old_versions = ["2.4.3", "2.3.3"]
    OLD_VERSION = False
    if any(version in config.madgraph["version"] for version in old_versions):
        OLD_VERSION = True
        log.warning(f"Old madgraph version detected.")

    output_path = Path(config.base["path"]).joinpath(config.base["output"]).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    # Ensure pythia card exists
    _pythia_card_path = Path(config.pythia["card"])
    if not _pythia_card_path.exists():
        log.error(f"{_pythia_card_path} does not exist.")
        sys.exit(1)

    pythia_config_path = f"/{_pythia_card_path}"

    # Controls whether to run Pythia8 or not
    pythia_onoff = "Pythia8"
    if config.pythia["skip"]:
        pythia_onoff = "OFF"
        pythia_config_path = ""

    substitution = dict(
        ecms=float(config.madgraph["ecms"]) / 2,
        nevents=int(config.madgraph["nevents"]),
        iseed=int(config.madgraph["seed"]),
    )

    masses = config.madgraph.get("masses", {})
    if any(key in masses for key in substitution.keys()):
        raise ValueError("Particles cannot be named ecms, nevents, or iseed.")

    substitution.update(masses)

    log.info("The following values will be substituted in where possible:")
    for key, value in substitution.items():
        log.info(f"    ${key} = {value}")

    # Update the param card
    param_card_path = Path(config.madgraph["paramcard"]).resolve()
    new_param_card_path = output_path.joinpath(param_card_path.name)
    log.info(f"Param Card: {new_param_card_path}")

    new_param_card_path.write_text(
        Template(param_card_path.read_text()).substitute(substitution)
    )

    # Update the run card
    run_card_path = Path(config.madgraph["run"]["card"]).resolve()
    if OLD_VERSION:
        log.warning("Changing the run card due to old madgraph version.")
        run_card_path = run_card_path.parent.joinpath("default_LO_oldformat.dat")
    new_run_card_path = output_path.joinpath(run_card_path.name)
    log.info(f"Run Card: {new_run_card_path}")

    # -- first do global opts
    new_run_card_path.write_text(
        Template(run_card_path.read_text()).substitute(substitution)
    )

    # -- now specific opts.  may want to reverse this order at some point, and do the specific before global.
    # Note: this will only work with options in the run card that contain a "!" in the line, indicating a comment at the end of the line.
    run_options = config.madgraph["run"].get("options", {})

    pattern = re.compile(
        r"^\s*(?P<value>[^\s]+)\s*=\s*(?P<key>[a-z_0-9]+)\s*\!.*$", re.DOTALL
    )
    with in_place.InPlace(new_run_card_path) as fp:
        for line in fp:
            match = pattern.match(line)
            if match:
                groups = match.groupdict()
                span = match.span("value")
                newvalue = str(run_options.pop(groups["key"], groups["value"]))
                # update the line based on input from the user, default to what is in the file
                line = line[: span[0]] + newvalue + line[span[1] :]
                if not newvalue == groups["value"]:
                    log.info(
                        f"    replacing value for {groups['key']}: {groups['value']} -> {newvalue}"
                    )
            fp.write(line)

    unused_keys = list(run_options.keys())
    if unused_keys:
        log.error(f"Unused keys supplied by you: {unused_keys}")
        raise KeyError(unused_keys[0])

    # Copy the proc card
    proc_card_path = Path(config.madgraph["proc"]["card"]).resolve()
    new_proc_card_path = output_path.joinpath(proc_card_path.name)
    log.info(f"Process Card: {new_proc_card_path}")

    shutil.copyfile(proc_card_path, new_proc_card_path)

    # Create the madgraph configuration card
    mgconfig_card_path = output_path.joinpath("run.mg5")
    log.info(f"MadGraph Config: {mgconfig_card_path}")

    # Figure out the run_mode.  0=single core, 1=cluster, 2=multicore.
    if config.madgraph["batch"]:
        run_mode = "set run_mode 0"  # we don't have MadGraph launch cluster jobs for us, we handle that ourselves.
    elif int(config.madgraph["cores"]) > 0:
        run_mode = "set run_mode 2\nset nb_core %d" % int(config.madgraph["cores"])
    else:
        run_mode = "set run_mode 2\nset nb_core %d" % int(
            multiprocessing.cpu_count() / 2
        )

    # figure out if running with madspin or not, and if so, put the card in the right place
    madspin_onoff = "OFF"
    madspin_config_path = ""
    if not config.madspin["skip"]:
        # Copy the madspin card
        madspin_card_path = Path(config.madspin.card).resolve()
        new_madspin_card_path = output_path.joinpath("madspin_card.dat")
        log.info(f"MadSpin Card: {new_madspin_card_path}")
        shutil.copyfile(madspin_card_path, new_madspin_card_path)
        madspin_onoff = "ON"
        madspin_config_path = f"/data/{new_madspin_card_path.name}"

    mg5config = f"""
{run_mode}
launch PROC_madgraph
madspin={madspin_onoff}
shower={pythia_onoff}
reweight=OFF
{madspin_config_path}
/data/{new_param_card_path.name}
/data/{new_run_card_path.name}
{pythia_config_path}
set iseed {config.madgraph['seed']}
done
"""
    if OLD_VERSION:
        mg5config = f"""
{run_mode}
launch PROC_madgraph
madspin={madspin_onoff}
reweight=OFF
{madspin_config_path}
/data/{new_param_card_path.name}
/data/{new_run_card_path.name}
done
"""

    with mgconfig_card_path.open(mode="w") as fp:
        for proc_line in new_proc_card_path.open():
            if not proc_line.strip():
                continue
            if proc_line.startswith("output"):
                proc_line = f"output PROC_madgraph\n"
            fp.write(proc_line)
        fp.write(mg5config)
