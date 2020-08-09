#!/usr/bin/env python

#### This just reads from the truth particle branch and plots the di-tau invariant mass (TRUTH!)
#### You can examine the Delphes tree by doing:
#### $: root <input_file>
#### [0]: TBrowser t
#### This will spawn a window for you to click around and see the contents and even do simple plots

#### You can "safely" ignore the warnings about the missing dictionaries...

import sys
import ROOT
import math
import array
import argparse
import os
from HistCollections import *

parser = argparse.ArgumentParser()
parser.add_argument('--input', action='store', default="input.txt")
parser.add_argument('--output', action='store', default="hist.root")
parser.add_argument('--lumi',action='store', default=3000000.) # 3 ab-1
parser.add_argument('--debug',action='store_true')
args=parser.parse_args()

chain = ROOT.TChain("Delphes")

if ( args.input[-4:] == 'root' ):
  print ( "Running over single root file:" )
  print ( "   > %s" % args.input )
  chain.Add(args.input)
else:
  print ( "Running over list of root files:" )
  for line in open(args.input):
    print ("   > " + line.rstrip('\n'))
    chain.Add(line.rstrip('\n'))

numFiles=chain.GetNtrees()
print ( "Loaded %s chains..." % numFiles )

#Make sure that the interpreter points to the DELPHES classes in order to read through DELPHES events.
# may need to run something like: export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:/home/mhance/Delphes/Delphes-3.4.1/:/home/mhance/Delphes/Delphes-3.4.1/external/
delphespath=os.environ.get('DELPHES_PATH')
ROOT.gInterpreter.Declare("#include \"%s/classes/DelphesClasses.h\"" % delphespath)
ROOT.gInterpreter.Declare("#include \"%s/external/ExRootAnalysis/ExRootTreeReader.h\"" % delphespath)
ROOT.gSystem.Load("%s/libDelphes.so" % delphespath)

# Import mT2 calculator
# ROOT.gSystem.Load("/export/share/diskvault2/mhance/PhenoPaper2018/Ana/CalcGenericMT2/src/libBinnedLik.so")

# Prevent the canvas from displaying
ROOT.gROOT.SetBatch(True)

# a histogram for our output
outfile=ROOT.TFile.Open(args.output,"RECREATE")

# Book histograms
allev=Hists("allev",outfile)
presel=Hists("presel",outfile)
SR=Hists("SR",outfile)
SR_jetbins=JetBins("SR_jetbins",outfile)

### Loop through all events in chain
entry = 0
for event in chain :
  entry += 1

  if ( entry != 0 and entry%1000 == 0 ):
    print ("%d events processed" % entry)

  # wrapper around Delphes events to make some things easier
  de=DelphesEvent(event)
  weight=de.weight*args.lumi/numFiles

  # fill histograms for all events
  allev.fill(de,weight)

  # preselection: 1 lepton, 1 b-jets, 1 tau
  if len(de.elecs)+len(de.muons)<1:
    continue
  if len(de.tautags)==0 or len(de.btags)==0:
    continue
  presel.fill(de,weight)
  
  # SR: 1 b-jets, 2 taus
  if len(de.tautags) != 2:
    continue
  if len(de.btags) != 1:
    continue
  SR.fill(de,weight)
  SR_jetbins.fill(de,weight)
    
allev.write()
presel.write()
SR.write()
SR_jetbins.write()
outfile.Close()
  
print ("Done!")
