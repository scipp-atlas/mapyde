#!/bin/bash
#set -e # exit when any command fails

nevents=10000
cores=8
seed=0
analysis="EwkCompressed2018"
likelihood="Slepton_bkgonly"
pythia_card="/cards/pythia/pythia8_card.dat"
delphes_card="delphes_card_ATLAS_lowptleptons.tcl"
ptj1min=100
deltaeta=0
mmjj=0.0
suffix="J${ptj1min}"
XSoverride=""

ecms=13
mass=150
masssplitting=5

# to run sleptons.  make sure we set "-n" in the options below.
proc="isrslep"
params="SleptonBino"

./run_VBFSUSY_standalone.sh \
    -E ${ecms} \
    -M ${mass} \
    -P ${proc} \
    -c ${cores} \
    -m ${mmjj} \
    -e ${deltaeta} \
    -p ${params} \
    -S ${masssplitting} \
    -N ${nevents} \
    -d ${seed} \
    -J ${ptj1min} \
    -i \
    -y ${pythia_card} \
    -L ${delphes_card} \
    -f ${analysis} \
    -F ${likelihood} \
    -h "${XSoverride}" \
    -s ${suffix} \
    -n \
    -I "-2.9" \
    ${skipopts}
