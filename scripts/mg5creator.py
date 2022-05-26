#!/usr/bin/env python3
import argparse
import shutil
from string import Template
from pathlib import Path
import pprint
import in_place
import re
import logging
import multiprocessing

logging.basicConfig(format="[%(levelname)s] %(message)s (%(filename)s:%(lineno)d)")
logging.getLogger().setLevel(logging.INFO)
log = logging.getLogger("mg5creator")

parser = argparse.ArgumentParser(description="Process some arguments.")

# Cards for the MadGraph run
parser.add_argument(
    "-r", "--run", default="cards/run/default_LO.dat", help="path to MG5 run card"
)
parser.add_argument("-P", "--proc", help="path to MG5 proc card")
parser.add_argument("-T", "--skippythia", action='store_true', help="skip running pythia, only run parton-level generation")
parser.add_argument("-g", "--overwrite", action='store_true', help="overwrite existing config files")
parser.add_argument("-S", "--madspin", help="path to MG5 madspin card", default=None)
parser.add_argument(
    "-p", "--param", default="cards/param/Higgsino.slha", help="path to SLHA/param card"
)
parser.add_argument(
    "-y",
    "--pythia",
    default="pythia8_card.dat",
    help="pythia card to use, must be in cards/pythia",
)

# Options for customizing the run
parser.add_argument(
    "-m", "--mass", action="append", nargs=2, help="pass in like '-m MN1 150'"
)
parser.add_argument(
    "-E", "--sqrts", default=13000.0, help="Center of mass energy, in GeV"
)
parser.add_argument("-n", "--numev", default=10000, help="Number of events to process")
parser.add_argument(
    "-R", "--runoption", action="append", nargs=2, help="pass in like '-R ptj 20'"
)

# Tag for this run
parser.add_argument("-t", "--tag", default="run", help="name for the job")

# Random seed for this job
parser.add_argument("-s", "--seed", default=0, help="random seed")

# control the number of cores for this job
parser.add_argument(
    "-c", "--cores", default=0, help="number of cores to use for madgraph and pythia"
)

# set batch/cluster mode, limits number of cores to 1, and overrides -c
parser.add_argument(
    "-b", "--batch", action="store_true", help="set batch mode, only uses a single core"
)

parser.add_argument(
    "-o", "--output", default="output", help="output directory for generated files"
)

parser.add_argument(
    "-I", "--MGversion", default="2.9.9", help="version of MadGraph to run"
)

args = parser.parse_args()

# Ensure directory exists
output_path = Path(args.output).joinpath(args.tag).resolve()
try:
    output_path.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    if args.overwrite:
        log.warning(
            f"{args.tag} is already used, overwriting existing configuration in that directory."
        )
    else:
        log.error(
            f"{args.tag} is already used, pick another tag or delete the directory: {output_path}."
        )
        exit(1)

# Ensure pythia card exists
_pythia_card_path = Path("cards/pythia").joinpath(args.pythia)
if not _pythia_card_path.exists():
    log.error(f"{_pythia_card_path} does not exist.")
    exit(1)

pythia_config_path=f"/cards/pythia/{args.pythia}"

# Controls whether to run Pythia8 or not
pythia_onoff="Pythia8"
if args.skippythia:
    pythia_onoff="OFF"
    pythia_config_path=""

substitution = dict(
    ecms=float(args.sqrts) / 2, nevents=int(args.numev), iseed=int(args.seed)
)

if args.mass:
    for particle, mass in args.mass:
        if particle in substitution:
            raise KeyError(f"{particle} cannot be redefined.")
        substitution[particle] = float(mass)

log.info("The following values will be substituted in where possible:")
for key, value in substitution.items():
    log.info(f"    ${key} = {value}")

# Update the param card
param_card_path = Path(args.param).resolve()
new_param_card_path = output_path.joinpath(param_card_path.name)
log.info(f"Param Card: {new_param_card_path}")

new_param_card_path.write_text(
    Template(param_card_path.read_text()).substitute(substitution)
)

# Update the run card
run_card_path = Path(args.run).resolve()
new_run_card_path = output_path.joinpath(run_card_path.name)
log.info(f"Run Card: {new_run_card_path}")

# -- first do global opts
new_run_card_path.write_text(
    Template(run_card_path.read_text()).substitute(substitution)
)

# -- now specific opts.  may want to reverse this order at some point, and do the specific before global.
# Note: this will only work with options in the run card that contain a "!" in the line, indicating a comment at the end of the line.
if args.runoption:
    runsubstitution = dict(args.runoption)
    pattern = re.compile(
        r"^\s*(?P<value>[^\s]+)\s*=\s*(?P<key>[a-z_0-9]+)\s*\!.*$", re.DOTALL
    )
    with in_place.InPlace(new_run_card_path) as fp:
        for line in fp:
            match = pattern.match(line)
            if match:
                groups = match.groupdict()
                span = match.span("value")
                newvalue = runsubstitution.pop(groups["key"], groups["value"])
                # update the line based on input from the user, default to what is in the file
                line = line[: span[0]] + newvalue + line[span[1] :]
                if not newvalue == groups["value"]:
                    log.info(
                        f"    replacing value for {groups['key']}: {groups['value']} -> {newvalue}"
                    )
            fp.write(line)

    unused_keys = list(runsubstitution.keys())
    if unused_keys:
        log.error(f"Unused keys supplied by you: {unused_keys}")
        raise KeyError(unused_keys[0])

# Copy the proc card
proc_card_path = Path(args.proc).resolve()
new_proc_card_path = output_path.joinpath(proc_card_path.name)
log.info(f"Process Card: {new_proc_card_path}")

shutil.copyfile(proc_card_path, new_proc_card_path)

# Create the madgraph configuration card
mgconfig_card_path = output_path.joinpath("run.mg5")
log.info(f"MadGraph Config: {mgconfig_card_path}")

# Figure out the run_mode.  0=single core, 1=cluster, 2=multicore.
if args.batch:
    run_mode = "set run_mode 0"  # we don't have MadGraph launch cluster jobs for us, we handle that ourselves.
elif int(args.cores) > 0:
    run_mode = "set run_mode 2\nset nb_core %d" % int(args.cores)
else:
    run_mode = "set run_mode 2\nset nb_core %d" % int(multiprocessing.cpu_count() / 2)

# figure out if running with madspin or not, and if so, put the card in the right place
madspin_onoff = "OFF"
madspin_config_path=""
if args.madspin:
    # Copy the madspin card
    madspin_card_path = Path(args.madspin).resolve()
    new_madspin_card_path = output_path.joinpath("madspin_card.dat")
    log.info(f"MadSpin Card: {new_madspin_card_path}")
    shutil.copyfile(madspin_card_path, new_madspin_card_path)
    madspin_onoff = "ON"
    madspin_config_path=f"/data/{new_madspin_card_path.name}"

config = f"""
{run_mode}
launch PROC_madgraph
madspin={madspin_onoff}
shower={pythia_onoff}
reweight=OFF
{madspin_config_path}
/data/{new_param_card_path.name}
/data/{new_run_card_path.name}
{pythia_config_path}
set iseed {args.seed}
done
"""

if "2.4.3" in args.MGversion or "2.3.3" in args.MGversion:
    config  = f"""
{run_mode}
launch PROC_madgraph
madspin={madspin_onoff}
reweight=OFF
{madspin_config_path}
/data/{new_param_card_path.name}
/data/{new_run_card_path.name}
done
"""


with mgconfig_card_path.open(mode="w") as mg5config:
    for proc_line in new_proc_card_path.open():
        if not proc_line.strip():
            continue
        if proc_line.startswith("output"):
            proc_line = f"output PROC_madgraph\n"
        mg5config.write(proc_line)
    mg5config.write(config)
