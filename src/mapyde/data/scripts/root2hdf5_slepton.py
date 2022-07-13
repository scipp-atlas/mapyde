from __future__ import annotations

import sys

import awkward as ak
import h5py
import numpy as np
import uproot

# input filename like "myrootfile.root:path/to/mytree"

infileandtree = sys.argv[1]
infile = infileandtree[: infileandtree.find(":")]
intree = infileandtree[infileandtree.find(":") + 1 :]

tree = uproot.open(infileandtree)
branches = tree.arrays()

mask = (
    (branches["met_Et"] > 200)
    & (branches["nLep_signal"] == 2)
    & (branches["lep1Flavor"] == branches["lep2Flavor"])
    & (branches["lep1Charge"] == -1 * branches["lep2Charge"])
    & (branches["nLep_base"] == 2)
    & (branches["met_Et"] / branches["METOverJ1pT"] > 100)
    & (branches["DPhiJ1Met"] > 2.0)
    & (branches["nJet30"] < 3)
    & (branches["nJet30"] > 0)
    & (branches["minDPhiAllJetsMet"] > 0.4)
    & (branches["nBJet20"] == 0)
    & (branches["lep1Pt"] > 10)
    & (branches["lep2Pt"] > 10)
    & (branches["Rll"] > 0.75)
    & (branches["mt_lep1"] > 10)
    & (branches["mt_lep2"] > 10)
)

branches_to_keep = [
    "lep1Flavor",
    "lep1Charge",
    "lep1Pt",
    "lep1Eta",
    "lep1Phi",
    "lep1MT_Met",
    "lep1_DPhiMet",
    "lep1Signal",
    "mt_lep1",
    "lep2Flavor",
    "lep2Charge",
    "lep2Pt",
    "lep2Eta",
    "lep2Phi",
    "lep2MT_Met",
    "lep2_DPhiMet",
    "lep2Signal",
    "mt_lep2",
    "Rll",
    "Ptll",
    "nJet30",
    "nBJet30",
    "jetPt",
    "jetEta",
    "jetPhi",
    "jetBtagged",
    "met_Et",
    "met_Phi",
    "METOverHT",
    "METOverHTLep",
    "minDPhiAllJetsMet",
    "MTauTau",
    "mt2leplsp_100",
]

n_events_after_mask = len(branches["nJet30"][mask])
print(n_events_after_mask)
print(len(branches))

outputbranches = []
for bname in branches[0].tolist().keys():
    if bname not in branches_to_keep:
        continue
    if bname[0:3] != "jet":
        if bname[0] == "n":
            outputbranches.append((bname, int))
        else:
            outputbranches.append((bname, float))
    else:
        for i in range(5):
            outputbranches.append((bname[0:3] + str(i) + bname[3:], float))


dt = np.dtype(outputbranches)

with h5py.File(infile.replace(".root", "__" + intree + ".hf5"), "w") as hdf5file:

    data = hdf5file.create_dataset(
        intree,
        (n_events_after_mask,),
        dtype=dt,
    )
    for bname in branches[0].tolist().keys():
        if bname not in branches_to_keep:
            continue

        if bname == "truthTauFromW_DMV":
            continue

        # flatten jet info
        if bname[0:3] == "jet":
            print(bname)
            num_entries = ak.num(branches[bname][mask], 0)

            # first supplement the data with dummy values.
            jetbranchdata = {}
            for i in range(5):
                newbname = bname[0:3] + str(i) + bname[3:]
                jetbranchdata[newbname] = []

            # loop over all events
            for j in range(num_entries):

                # print("=====================================================")
                # print(len(branches[bname][j]))
                num_jets = ak.count(branches[bname][mask][j], 0)
                # print("%6d" % j)
                # print(branches[bname][j])
                # print(num_jets)

                # take the data that's there
                for i in range(min(5, num_jets)):
                    newbname = bname[0:3] + str(i) + bname[3:]
                    jetbranchdata[newbname].append(branches[bname][mask][j][i])

                # add dummy data as needed
                for i in range(num_jets, 5):
                    newbname = bname[0:3] + str(i) + bname[3:]
                    jetbranchdata[newbname].append(-9)

                # if j<5:
                #    for i in range(5):
                #        print(jetbranchdata[bname[0:3]+str(i)+bname[3:]])
                #    print("=====================================================")
                # else:
                #    break

            # print(len(jetbranchdata[bname[0:3]+str(0)+bname[3:]]))
            # now fill them into HDF5 structure
            for i in range(5):
                newbname = bname[0:3] + str(i) + bname[3:]
                data[newbname] = jetbranchdata[newbname]
        else:
            # continue
            data[bname] = branches[bname][mask]
