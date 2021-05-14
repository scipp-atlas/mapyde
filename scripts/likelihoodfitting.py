import json
import jsonpatch
import pathlib
import copy
import argparse
import cabinetry
import shutil
import os

# patch the background-only fit
parser = argparse.ArgumentParser(description="Process some arguments.")

# Cards for the MadGraph run
parser.add_argument("-s", "--signal", help="path to signal patch file")
parser.add_argument("-b", "--background", help="path to JSON background-only file")
parser.add_argument("-n", "--name", help="name of signal sample")
args = parser.parse_args()

with open(args.background) as f:
    bgonly=json.load(f)
with open(args.signal) as f:
    signal=json.load(f)

res=jsonpatch.apply_patch(bgonly, signal)

#print(json.dumps(res, indent=4, sort_keys=True))
jsonws=args.name + "__" + args.background.replace("_bkgonly","")
with open(jsonws, 'w') as f:
    json.dump(res, f, sort_keys=True, indent=4)



shutil.rmtree("cabinetry_figs")
os.mkdir("cabinetry_figs")

# build a workspace
ws = cabinetry.workspace.load(jsonws)
# run a fit
model, data = cabinetry.model_utils.model_and_data(ws)
fit_results = cabinetry.fit.fit(model, data); # remove semicolon to see more output
# This part may take some time, depending on how complicated the workspace is.
limit_results = cabinetry.fit.limit(model, data)
cabinetry.visualize.limit(limit_results)
print(limit_results.observed_limit)
print(limit_results.expected_limit)
import pyhf
pyhf.infer.test_statistics.q0
p_observed,p_expected = pyhf.infer.hypotest(1.0, data, model, test_stat='q0', return_expected=True)
import scipy
scipy.stats.norm.isf(p_expected, 0, 1)
