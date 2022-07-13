from __future__ import annotations

import argparse
import subprocess

import pyhepmc_ng as hep

parser = argparse.ArgumentParser(description="Process some arguments.")

parser.add_argument("-b", "--base", default="output", help="name for the job")
parser.add_argument("-t", "--tag", default="run", help="name for the job")
parser.add_argument(
    "-c",
    "--cores",
    type=int,
    default=1,
    help="number of cores available for delphes, i.e. how many output files there should be.",
)

args = parser.parse_args()
madgraphpath = "madgraph/PROC_madgraph/Events/run_01/"
orighepmc = "tag_1_pythia8_events.hepmc"
newhepmc = "tag_1_pythia8_events_%d.hepmc"

inputfile = f"{args.base}/{args.tag}/{madgraphpath}/{orighepmc}"

# figure out how many events in the input .hepmc file.
proc = subprocess.Popen(
    ['grep "E " %s | wc' % inputfile], shell=True, stdout=subprocess.PIPE
)
stdout, stderr = proc.communicate()
numev = int(stdout.decode("utf-8").split()[0])

# calculate the number of events to put in each output file
neventsperfile = int(numev / args.cores) + 1

outfiles = {}

with hep.open(inputfile) as f:
    evtcount = 0
    filecounter = -1
    evt = hep.GenEvent()
    while not f.failed():
        if evtcount % neventsperfile == 0:
            filecounter += 1
            outputfile = "{}/{}/{}/{}".format(
                args.base,
                args.tag,
                madgraphpath,
                newhepmc % filecounter,
            )
            outfiles[filecounter] = hep.open(outputfile, "w")
        ok = f.read_event(evt)
        outfiles[filecounter].write(evt)
        evtcount += 1
