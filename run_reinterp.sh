#!/bin/bash
#set -e # exit when any command fails

nevents=50000
cores=8
seed=0
analysis="EwkCompressed2018"
likelihood="Slepton_bkgonly"
pythia_card="pythia8_card.dat"
delphes_card="delphes_card_ATLAS_lowptleptons.tcl"
ptj1min=100
deltaeta=0
mmjj=0.0
suffix="J${ptj1min}"
XSoverride=""

clobber_mgpy=false
clobber_delphes=false
clobber_ana=false

ecms=13
mass=125
masssplitting=20

# to run sleptons.  make sure we set "-n" in the options below.
proc="isrslep"
params="SleptonBino"

while getopts "E:M:S:N:c:d:f:P:p:J:L:F:s:gla" opt; do
    case "${opt}" in
	E) ecms=$OPTARG;;
	M) mass=$OPTARG;;
	P) proc=$OPTARG;;
	p) params=$OPTARG;;
	N) nevents=$OPTARG;;
	s) suffix=$OPTARG;;
	c) cores=$OPTARG;;
	g) clobber_mgpy=true;;
	l) clobber_delphes=true;;
	a) clobber_ana=true;;
	J) ptj1min=$OPTARG;;
	S) masssplitting=$OPTARG;;
	d) seed=$OPTARG;;
	L) delphescard=$OPTARG;;
	f) simpleanalysis=$OPTARG;;
	F) likelihood=$OPTARG;;
	\?) echo "Invalid option: -$OPTARG";;
    esac
done


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
