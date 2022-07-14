#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys

import matplotlib
import ROOT

matplotlib.use("TkAgg")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    action="store",
    default="/data/users/mhance/SUSY/VBFSUSY_13_Higgsino_150_mjj_all.root",
)
parser.add_argument("--inputTree", action="store", default="allev/hftree")
parser.add_argument("--output", action="store", default="hist.root")
parser.add_argument("--lumi", action="store", default=1000.0)  # 1 fb-1
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

chain = ROOT.TChain(args.inputTree)

if args.input[-4:] == "root":
    print("Running over single root file:")
    print("   > %s" % args.input)
    chain.Add(args.input)
else:
    print("Running over list of root files:")
    for line in open(args.input):
        print("   > " + line.rstrip("\n"))
        chain.Add(line.rstrip("\n"))

numFiles = chain.GetNtrees()
print("Loaded %s chains..." % numFiles)

# Prevent the canvas from displaying
# ROOT.gROOT.SetBatch(True)

# a histogram for our output
outfile = ROOT.TFile.Open(args.output, "RECREATE")

# make a histogram
h_MET = ROOT.TH1F("MET", "MET", 100, 0, 1000)

# make an array to keep MET vals for matplotlib
# a_MET = []
# a_weights = []

# Loop through all events in chain
entry = 0
for event in chain:
    entry += 1

    if entry != 0 and entry % 10000 == 0:
        print("%d events processed" % entry)
        sys.stdout.flush()

    # this is how we know how much this event "counts" when looking at large collections of events.
    weight = event.weight / numFiles

    # missing transverse energy (MET)
    MET = event.MET

    # require event to have some properties.
    # if event.mjj > 100:
    #   # if the event passes, fill the histogram.
    #   h_MET.Fill(MET,weight)
    #   a_MET.append(MET)
    #   a_weights.append(weight)

# show the ROOT output on a TCanvas.  To get the canvas to show up while running the script,
# make sure to run in interactive python mode: "python -i FlatAna.py --input ..."
canvas = ROOT.TCanvas("MET_canvas", "MET canvas", 800, 600)
canvas.SetLogy(ROOT.kTRUE)
h_MET.Draw()

# write the histogram to the output file.
h_MET.Write()

# # show a matplotlib example
# plt.hist(np.array(a_MET),bins=100,range=(0,1000),density=1,weights=np.array(a_weights))
# #plt.show()

# close the output file.
# outfile.Close()

print("Done!")
