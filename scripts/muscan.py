#### #!/home/kratsg/venv/bin/python3

import pyhf
import json
import jsonpatch
import numpy as np
import matplotlib.pyplot as plt
import argparse
from pyhf.contrib.viz import brazil

parser = argparse.ArgumentParser(description="Process some arguments.")
parser.add_argument("-s", "--signal", help="name of analysis")
parser.add_argument("-b", "--background", help="path to JSON background-only file")
parser.add_argument("-n", "--tag", default="SUSY_13_Higgsino_101_isrinc_J125", help="tag for data files")
parser.add_argument("-c", "--cpu", action='store_true', help="do not use a GPU even if available.  Sets backend to NumPy instead.")
parser.add_argument("-B", "--backend", default="numpy", help="choose backend for pyhf.  Jax will be used if running with a GPU.")
args = parser.parse_args()

ana=args.signal.replace("_patch.json","")
tag=args.tag

if args.cpu:
    pyhf.set_backend(args.backend, pyhf.optimize.minuit_optimizer(tolerance=0.01)) # monojet uses 0.001
else:
    # useful when running on a machine with a GPU
    pyhf.set_backend("jax", pyhf.optimize.minuit_optimizer(tolerance=0.01)) # monojet uses 0.001

with open(args.background) as f:
    bgonly=json.load(f)
with open(args.signal) as f:
    signal=json.load(f)

spec=jsonpatch.apply_patch(bgonly, signal)

ws = pyhf.Workspace(spec)
pdf = ws.model()

observations = ws.data(pdf)

poi_values = np.linspace(0.1, 2, 10)

init_pars = pdf.config.suggested_init()
init_pars[pdf.config.poi_index] = 1.0

results = [
    pyhf.infer.hypotest(poi_value, observations, pdf, init_pars=init_pars, test_stat="qtilde", return_expected_set=True)
    for poi_value in poi_values
]
# obs_limit, exp_limits, (scan, results) = pyhf.infer.intervals.upperlimit(observations, pdf, poi_values, level=0.05, return_results=True)
fig, ax = plt.subplots()
brazil.plot_results(ax, poi_values, results)
fig.savefig(f'muscan_{tag}__{ana}.pdf')
