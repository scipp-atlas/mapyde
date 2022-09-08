from __future__ import annotations

import argparse
import copy
import json

import jsonpatch
import pyhf
import uproot

parser = argparse.ArgumentParser(description="Process some arguments.")

# Cards for the MadGraph run
parser.add_argument(
    "-i",
    "--input",
    action="append",
    help="path to SA output.  can be used multiple times if merging files.",
)
parser.add_argument("-b", "--background", help="path to JSON background-only file")
parser.add_argument("-o", "--output", help="path to JSON output")
parser.add_argument("-n", "--name", help="name of signal sample")
parser.add_argument("-l", "--lumi", help="luminosity in pb-1")
parser.add_argument(
    "-c",
    "--compressed",
    action="store_true",
    help="special selection for compressed searches",
)
args = parser.parse_args()

print("Using luminosity=%f" % float(args.lumi))
if args.compressed:
    print("Applying ee/mm masks to SA output as needed")


def JSONtoSA(SRname, background):
    """this function converts the name of the SR in the serialized likelihood into
    the name of the SR in the SimpleAnalysis output
    """

    SRname_split = SRname.split("_")
    if "CR" in SRname_split[0]:
        return None

    if "MonoJet" in background:
        return SRname.replace("_cuts", "")

    # otherwise we're in Compressed?

    SAname = "SR"
    if "MT2" in SRname_split[1]:
        SAname += "_S_"
        if "hghmet" in SRname_split[2]:
            SAname += "high_"
        elif "lowmet" in SRname_split[2] and "MT2" in SRname_split[1]:
            SAname += "low_"
        SAname += SRname_split[1]
    else:
        SAname += "_E_"
        if "Onelep1track" in SRname_split[2]:
            SAname += "lT_"
        elif "hghmet" in SRname_split[2]:
            SAname += "high_"
        elif "lowmet" in SRname_split[2] and "low" in SRname_split[4]:
            SAname += "med_"
        elif "lowmet" in SRname_split[2] and "high" in SRname_split[4]:
            SAname += "low_"
        SAname += SRname_split[1]

    return SAname


with open(args.background) as f:
    spec = json.load(f)
    newspec = copy.deepcopy(spec)
    ws = pyhf.Workspace(spec)

rootfiles = [uproot.open(i) for i in args.input]
trees = [r["ntuple"] for r in rootfiles]
branchsets = [t.arrays() for t in trees]

# loop over all channels in the workspace and update them where appropriate.
for channel in ws.channels:

    c_index = ws.channels.index(channel)
    SAname = JSONtoSA(channel, args.background)
    if SAname is None:
        continue

    yld = 0

    # only do something if the SA output has a field for this
    # particular signal region.
    for tree, branches in zip(trees, branchsets):
        if SAname in tree.keys():
            mask = branches[SAname] > 0
            if args.compressed:
                # in the Compressed SA output, the SR's are not broken down
                # by flavor, while in the serialized likelihood they are.
                # use the fields in the ntuple to do the flavor breakdown here.

                flavname = "isee" if "ee" in channel else "ismm"
                mask = (branches[SAname] > 0) & (branches[flavname] > 0)

            yld += sum(branches[SAname][mask])

    yld *= float(args.lumi)
    print("%3d  %40s  %40s  %.2e" % (c_index, channel, SAname, yld))

    newspec["channels"][c_index]["samples"].append(
        {
            "name": args.name,
            "data": [yld],
            "modifiers": [{"name": "mu_SIG", "type": "normfactor", "data": None}],
        }
    )

patch = jsonpatch.make_patch(spec, newspec)

with open(args.output, "w") as f:
    json.dump(patch.patch, f, sort_keys=True, indent=4)
