import argparse
import shutil
from string import Template
from pathlib import Path
import pprint

parser = argparse.ArgumentParser(description="Process some arguments.")

# Cards for the MadGraph run
parser.add_argument(
    "-r", "--run", default="cards/run/default_LO.dat", help="path to MG5 run card"
)
parser.add_argument("-P", "--proc", help="path to MG5 proc card")
parser.add_argument(
    "-p", "--param", default="cards/param/Higgsino.slha", help="path to SLHA/param card"
)
parser.add_argument(
    "-y", "--pythia", default="cards/pythia/pythia8_card.dat", help="path to pythia card"
)

# Options for customizing the run
parser.add_argument(
    "-m", "--mass", action="append", nargs=2, help="pass in like '-m MN1 150'"
)
parser.add_argument(
    "-E", "--sqrts", default=13000.0, help="Center of mass energy, in GeV"
)
parser.add_argument("-n", "--numev", default=10000, help="Number of events to process")

# Tag for this run
parser.add_argument("-t", "--tag", default="run", help="name for the job")

# Random seed for this job
parser.add_argument("-s", "--seed", default=0, help="random seed")

parser.add_argument(
    "-o", "--output", default="output", help="output directory for generated files"
)

args = parser.parse_args()

# Ensure directory exists
output_path = Path(args.output).joinpath(args.tag).resolve()
try:
    output_path.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    print(f"{args.tag} is already used, pick another tag or delete the directory.")
    exit(1)

substitution = dict(
    ecms=float(args.sqrts) / 2, nevents=int(args.numev), iseed=int(args.seed)
)

for particle, mass in args.mass:
    if particle in substitution:
        raise KeyError(f"{particle} cannot be redefined.")
    substitution[particle] = float(mass)

pprint.pprint(substitution)

# Update the param card
param_card_path = Path(args.param).resolve()
new_param_card_path = output_path.joinpath(param_card_path.name)

new_param_card_path.write_text(
    Template(param_card_path.read_text()).substitute(substitution)
)

# Update the run card
run_card_path = Path(args.run).resolve()
new_run_card_path = output_path.joinpath(run_card_path.name)

new_run_card_path.write_text(
    Template(run_card_path.read_text()).substitute(substitution)
)

# Copy the proc card
proc_card_path = Path(args.proc).resolve()
new_proc_card_path = output_path.joinpath(proc_card_path.name)
shutil.copyfile(proc_card_path, new_proc_card_path)

# Create the madgraph configuration card

# set run_mode 0   # mg5_configuration.txt
config = f"""
launch PROC_{args.tag}
shower=Pythia8
madspin=OFF
reweight=OFF
{new_param_card_path.name}
{new_run_card_path.name}
set iseed {args.seed}
done
"""

with output_path.joinpath("run.mg5").open(mode="w") as mg5config:
    for proc_line in new_proc_card_path.open():
        if not proc_line.strip():
            continue
        if proc_line.startswith("output"):
            proc_line = f"output PROC_{args.tag}\n"
        mg5config.write(proc_line)
    mg5config.write(config)
