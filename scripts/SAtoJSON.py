import json
import jsonpatch
import copy
import argparse
import uproot
import pyhf
import numpy as np

parser = argparse.ArgumentParser(description="Process some arguments.")

# Cards for the MadGraph run
parser.add_argument("-i", "--input", help="path to SA output")
parser.add_argument("-b", "--background", help="path to JSON background-only file")
parser.add_argument("-o", "--output", help="path to JSON output")
parser.add_argument("-n", "--name", help="name of signal sample")
args = parser.parse_args()

with open(args.background,'r') as f:
    spec = json.load(f)
    newspec = copy.deepcopy(spec)
    ws = pyhf.Workspace(spec)

rootfile = uproot.open(args.input)
tree=rootfile["ntuple"]
branches = tree.arrays()

# this function converts the name of the SR in the serialized likelihood into
# the name of the SR in the SimpleAnalysis output
def JSONtoSA(SRname):
    SRname_split=SRname.split("_")
    if "CR" in SRname_split[0]: return None
    
    SAname="SR"
    if "MT2" in SRname_split[1]:
        SAname+="_S_"
        if "hghmet" in SRname_split[2]:
            SAname+="high_"
        elif "lowmet" in SRname_split[2] and "MT2" in SRname_split[1]:
            SAname+="low_"
        SAname+=SRname_split[1]
    else:
        SAname+="_E_"
        if "Onelep1track" in SRname_split[2]:
            SAname+="lT_"
        elif "hghmet" in SRname_split[2]:
            SAname+="high_"
        elif "lowmet" in SRname_split[2] and "low" in SRname_split[4]:
            SAname+="med_"
        elif "lowmet" in SRname_split[2] and "high" in SRname_split[4]:
            SAname+="low_"
        SAname+=SRname_split[1]

    return SAname

# loop over all channels in the workspace and update them where appropriate.
for channel in ws.channels:

    c_index = ws.channels.index(channel)
    SAname=JSONtoSA(channel)
    if SAname is None: continue
    
    yld=0

    # only do something if the SA output has a field for this
    # particular signal region.
    if SAname in tree.keys():
        # in the Compressed SA output, the SR's are not broken down
        # by flavor, while in the serialized likelihood they are.
        # use the fields in the ntuple to do the flavor breakdown here.
        flavname="isee" if "ee" in channel else "ismm"
        mask=(branches[SAname]>0)&(branches[flavname]>0)
        yld=branches[SAname][mask][0]
    
    print(c_index, channel, SAname, yld)

    newspec['channels'][c_index]['samples'].append({'name': args.name, 'data': [yld], 'modifiers': [{'name': 'mu_SIG', 'type': 'normfactor', 'data': None}]})

patch = jsonpatch.make_patch(spec, newspec)

with open(args.output, 'w') as f:
    json.dump(patch.patch, f, sort_keys=True, indent=4)
