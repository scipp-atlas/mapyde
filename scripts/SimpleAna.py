#!/usr/bin/env python3

# You can "safely" ignore the warnings about the missing dictionaries...

from __future__ import annotations

import argparse
import os
import re
import sys

import ROOT
from HistCollections import DelphesEvent, Hists

parser = argparse.ArgumentParser()
parser.add_argument("--input", action="store", default="input.txt")
parser.add_argument("--output", action="store", default="hist.root")
parser.add_argument("--lumi", action="store", default=1000.0)  # 1 fb-1
parser.add_argument("--debug", action="store_true")
parser.add_argument("--XS", action="store", default=0)
args = parser.parse_args()


def strip_ansi_codes(s):
    """
    Remove ANSI color codes from the string.
    """
    return re.sub("\033\\[([0-9]+)(;[0-9]+)*m", "", s)


reweightEvents = False
XS = 0
if float(args.XS) > 0:
    XS = float(strip_ansi_codes(args.XS))
    print(XS)
    reweightEvents = True


chain = ROOT.TChain("Delphes")

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

# Make sure that the interpreter points to the DELPHES classes in order to read through DELPHES events.
# may need to run something like: export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:/home/mhance/Delphes/Delphes-3.4.1/:/home/mhance/Delphes/Delphes-3.4.1/external/
delphespath = os.environ.get("DELPHES_PATH")
ROOT.gInterpreter.Declare('#include "%s/classes/DelphesClasses.h"' % delphespath)
ROOT.gInterpreter.Declare(
    '#include "%s/external/ExRootAnalysis/ExRootTreeReader.h"' % delphespath
)
ROOT.gSystem.Load("%s/libDelphes.so" % delphespath)

# Import mT2 calculator
# ROOT.gSystem.Load("/export/share/diskvault2/mhance/PhenoPaper2018/Ana/CalcGenericMT2/src/libBinnedLik.so")

# Prevent the canvas from displaying
ROOT.gROOT.SetBatch(True)

# a histogram for our output
outfile = ROOT.TFile.Open(args.output, "RECREATE")

# Book histograms
allev = Hists("allev", outfile)
presel = Hists("presel", outfile)
SR = Hists("SR", outfile)
# SR_jetbins=JetBins("SR_jetbins",outfile)

weightscale = float(args.lumi) / numFiles
# Loop through all events in chain to get the sum of weights before filling trees and hists
# There should be a better way to do this....
if reweightEvents:
    print("Computing sum of weights")
    entry = 0
    sumofweights = 0
    for event in chain:
        entry += 1

        if entry != 0 and entry % 10000 == 0:
            print("%d events processed for sum of weights" % entry)
            sys.stdout.flush()

        # wrapper around Delphes events to make some things easier
        de = DelphesEvent(event)
        sumofweights += de.weight

    # compute appropriate weights for each event
    weightscale *= XS / sumofweights

# Loop through all events in chain
print("Processing events")
entry = 0
for event in chain:
    entry += 1

    if entry != 0 and entry % 10000 == 0:
        print("%d events processed" % entry)
        sys.stdout.flush()

    # wrapper around Delphes events to make some things easier
    de = DelphesEvent(event)
    weight = de.weight * weightscale

    # fill histograms for all events
    allev.fill(de, weight)

    # preselection: MET>120, >=2 jets
    if de.met.Pt() < 150 or len(de.jets) < 2:
        continue
    presel.fill(de, weight)

    # SR: zero e/mu/tau, deltaeta>3, mjj>1 TeV, nJets==2
    if len(de.tautags) != 0:
        continue
    if len(de.elecs) != 0:
        continue
    if len(de.muons) != 0:
        continue
    if len(de.exclJets) < 2:
        continue
    mjj = (de.exclJets[0].P4() + de.exclJets[1].P4()).M()
    if mjj < 1000:
        continue
    deta = abs(de.exclJets[0].P4().Eta() - de.exclJets[1].P4().Eta())
    if deta < 3.0:
        continue

    SR.fill(de, weight)
    # SR_jetbins.fill(de,weight)

allev.write()
presel.write()
SR.write()
# SR_jetbins.write()
outfile.Close()

print("Done!")
