#!/usr/bin/env python

import sys
import ROOT
import math
import array
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input', action='store', default="input.txt")
parser.add_argument('--inputTree', action='store', default="allev/hftree")
parser.add_argument('--output', action='store', default="hist.root")
parser.add_argument('--lumi',action='store', default=1000.) # 1 fb-1
parser.add_argument('--debug',action='store_true')
args=parser.parse_args()

chain = ROOT.TChain(args.inputTree)

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

# Prevent the canvas from displaying
ROOT.gROOT.SetBatch(True)

# a histogram for our output
outfile=ROOT.TFile.Open(args.output,"RECREATE")

# make a histogram
h_MET = ROOT.TH1F("MET","MET",100,0,1000)

### Loop through all events in chain
entry = 0
for event in chain:
  entry += 1

  if ( entry != 0 and entry%10000 == 0 ):
    print ("%d events processed" % entry)
    sys.stdout.flush()

  # this is how we know how much this event "counts" when looking at large collections of events.
  weight=event.weight/numFiles

  # missing transverse energy (MET)
  MET=event.MET

  # require event to have some properties.
  if event.mjj > 100:
    # if the event passes, fill the histogram.
    h_MET.Fill(MET,weight)

# write the histogram to the output file.
h_MET.Write()

# close the output file.
outfile.Close()
  
print ("Done!")
