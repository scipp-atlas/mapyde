from __future__ import annotations

import sys

import h5py
import numpy as np
import uproot

# input filename like "myrootfile.root:path/to/mytree"

infileandtree = sys.argv[1]
infile = infileandtree[: infileandtree.find(":")]
intree = infileandtree[infileandtree.find(":") + 1 :]

tree = uproot.open(infileandtree)
branches = tree.arrays()

dt = np.dtype(
    [
        (bname, int) if bname[0] == "n" else (bname, float)
        for bname in branches[0].tolist().keys()
    ]
)

with h5py.File(infile.replace(".root", ".hf5"), "w") as hdf5file:

    data = hdf5file.create_dataset(
        intree,
        (len(branches),),
        dtype=dt,
    )
    for bname in branches[0].tolist().keys():
        data[bname] = branches[bname]
