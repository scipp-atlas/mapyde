#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os

import jsonpatch
import numpy as np

os.environ["MPLCONFIGDIR"] = os.getcwd() + "/configs/"
import matplotlib.pyplot as plt  # noqa: E402

parser = argparse.ArgumentParser(description="Process some arguments.")
parser.add_argument("-s", "--signal", help="name of analysis")
parser.add_argument("-b", "--background", help="path to JSON background-only file")
parser.add_argument(
    "-n", "--tag", default="SUSY_13_Higgsino_101_isrinc_J125", help="tag for data files"
)
parser.add_argument(
    "-c",
    "--cpu",
    action="store_true",
    help="do not use a GPU even if available.  Sets backend to NumPy instead.",
)
parser.add_argument(
    "-B",
    "--backend",
    default="jax",
    help="choose backend for pyhf.  Jax will be used if running with a GPU.",
)
parser.add_argument(
    "-o",
    "--optimizer",
    default="scipy",
    help="choose optimizer.  'scipy', 'minuit' ....",
)
parser.add_argument(
    "-l",
    "--likelihood",
    default=None,
    help="pass in full likelihood, with both signal and background included.",
)
parser.add_argument("-p", "--plot", action="store_true", help="make a plot of the CLs")
args = parser.parse_args()

if args.cpu and args.backend == "jax":
    os.environ["JAX_PLATFORM_NAME"] = "cpu"

import pyhf  # noqa: E402
from pyhf.contrib.viz import brazil  # noqa: E402

tolerance = 1e-2  # 0.01 works most of the time, monojet uses 0.001

optimizer = args.optimizer
if optimizer == "minuit":
    optimizer = pyhf.optimize.minuit_optimizer(tolerance=tolerance)

pyhf.set_backend(args.backend, optimizer)
if not args.cpu:
    # useful when running on a machine with a GPU
    pyhf.set_backend("jax", optimizer)


# We can either pass in a full likelihood with signal+background already there, or pass in
# a background likelihood and a signal patch file.  If we do use a signal patch file, then
# write the full likelihood out to a file for reference later.
spec = None
if args.likelihood is None:
    with open(args.background) as f:
        bgonly = json.load(f)
    with open(args.signal) as f:
        signal = json.load(f)

    spec = jsonpatch.apply_patch(bgonly, signal)
    ana = args.signal.replace("_patch.json", "")
    with open(ana + ".json", "w") as f:
        f.write(json.dumps(spec, indent=4, sort_keys=True))

else:
    spec = json.load(open(args.likelihood))
    ana = args.likelihood.replace(".json", "")

ws = pyhf.Workspace(spec)
pdf = ws.model()

observations = ws.data(pdf)

poi_values = np.linspace(0.1, 2, 10)

init_pars = pdf.config.suggested_init()
init_pars[pdf.config.poi_index] = 1.0

print("running scan")

results = [
    pyhf.infer.hypotest(
        poi_value,
        observations,
        pdf,
        init_pars=init_pars,
        test_stat="qtilde",
        return_expected_set=True,
    )
    for poi_value in poi_values
]

print("printing results")

obs_limit, exp_limits, (scan, results) = pyhf.infer.intervals.upperlimit(
    observations, pdf, poi_values, level=0.05, return_results=True
)
print(f"Observed limit: {obs_limit}")
print("Expected limit: %5.3f" % exp_limits[2])
print("      -1 sigma: %5.3f" % exp_limits[1])
print("      +1 sigma: %5.3f" % exp_limits[3])
print("      -2 sigma: %5.3f" % exp_limits[0])
print("      +2 sigma: %5.3f" % exp_limits[4])

if args.plot:
    print("making plot")
    fig, ax = plt.subplots()
    brazil.plot_results(poi_values, results, ax=ax)
    fig.savefig(f"muscan_{args.tag}__{ana}.pdf")
