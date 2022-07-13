from __future__ import annotations

import sys

import matplotlib.pyplot as plt
import numpy as np
import uproot

signal = uproot.open("/data/users/mhance/SUSY/VBFSUSY_13_Higgsino_150_mjj_all.root")

tree = signal["allev/hftree"]
branches = tree.arrays(namedecode="utf-8")

numevents = len(branches["weight"])

# make an array to keep MET vals for matplotlib
a_MET = []
a_weights = []

# loop over events
entry = 0
for i in range(numevents):
    entry += 1

    if entry != 0 and entry % 10000 == 0:
        print("%d events processed" % entry)
        sys.stdout.flush()

    # this is how we know how much this event "counts" when looking at large collections of events.
    weight = branches["weight"][i]

    # missing transverse energy (MET)
    MET = branches["MET"][i]
    mjj = branches["mjj"][i]
    # require event to have some properties.
    if mjj > 100:
        # if the event passes, fill the histogram.
        a_MET.append(MET)
        a_weights.append(weight)

plt.hist(
    np.array(a_MET), bins=100, range=(0, 1000), density=1, weights=np.array(a_weights)
)
# plt.show()
