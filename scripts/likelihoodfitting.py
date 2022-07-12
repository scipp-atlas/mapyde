from __future__ import annotations

import argparse
import json
import os
import shutil

import cabinetry
import jsonpatch
import pyhf
import scipy

# pyhf.set_backend("jax")

# patch the background-only fit
parser = argparse.ArgumentParser(description="Process some arguments.")

# Cards for the MadGraph run
parser.add_argument("-s", "--signal", help="path to signal patch file")
parser.add_argument("-b", "--background", help="path to JSON background-only file")
parser.add_argument("-n", "--name", help="name of signal sample")
args = parser.parse_args()

with open(args.background) as f:
    bgonly = json.load(f)
with open(args.signal) as f:
    signal = json.load(f)

res = jsonpatch.apply_patch(bgonly, signal)

# print(json.dumps(res, indent=4, sort_keys=True))
jsonws = args.name + "__" + args.background.split("/")[-1].replace("_bkgonly", "")
with open(jsonws, "w") as f:
    json.dump(res, f, sort_keys=True, indent=4)


shutil.rmtree("cabinetry_figs", ignore_errors=True)
os.mkdir("cabinetry_figs")

# build a workspace
ws = cabinetry.workspace.load(jsonws)
model, data = cabinetry.model_utils.model_and_data(ws)

print(model)
print(data)

# run a fit
print("running one fit")
fit_results = cabinetry.fit.fit(ws)

# This part may take some time, depending on how complicated the workspace is.
print("running limits")
limit_results = cabinetry.fit.limit(model, data)

print("visualizing results")
cabinetry.visualize.limit(limit_results)
print(limit_results.observed_limit)
print(limit_results.expected_limit)

pyhf.infer.test_statistics.q0
p_observed, p_expected = pyhf.infer.hypotest(
    1.0, data, model, test_stat="q0", return_expected=True
)

scipy.stats.norm.isf(p_expected, 0, 1)
