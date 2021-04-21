#!/usr/bin/env python

#### You can "safely" ignore the warnings about the missing dictionaries...

import sys
import ROOT
import math
import array
import argparse
import os
import re
from HistCollections import *

parser = argparse.ArgumentParser()
parser.add_argument('--input', action='store', default="input.txt")
parser.add_argument('--output', action='store', default="hist.root")
parser.add_argument('--lumi',action='store', default=1000.) # 1 fb-1
parser.add_argument('--evtype',action='store',default=-1) # 0: tthh; 1: ttbb; 2: tth; 3: ttz
parser.add_argument('--XS',action='store',default=0)
parser.add_argument('--debug',action='store_true')
args=parser.parse_args()

def strip_ansi_codes(s):
    """
    Remove ANSI color codes from the string.
    """
    return re.sub('\033\\[([0-9]+)(;[0-9]+)*m', '', s) 

XS=float(strip_ansi_codes(args.XS))
print(XS)

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

# Make sure that the interpreter points to the DELPHES classes in order to read through DELPHES events.
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

# Make the output tree
allev=tthhTree("allev",outfile)

### Loop through all events in chain
entry = 0
Nevents=chain.GetEntries()
for event in chain :
  entry += 1

  if ( entry != 0 and entry%10000 == 0 ):
    print ("%d events processed" % entry)
    sys.stdout.flush()

  # wrapper around Delphes events to make some things easier
  de=DelphesEvent(event,highlumi=True)

  weight=de.weight

  # something stupid for sherpa.  this is not strictly correct, since
  # sherpa weights are not necessarily uniform.
  if XS!=0:
    weight=XS/Nevents

  weight=weight*float(args.lumi)/numFiles
  de.truth=int(args.evtype)

  # fill histograms for all events
  allev.fill(de,weight)

    
allev.write()
outfile.Close()
  
print ("Done!")
