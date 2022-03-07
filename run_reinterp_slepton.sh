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
kfactor=1.3
database=/data/users/${USER}/SUSY

clobber_mgpy=false
clobber_delphes=false
clobber_ana=false

ecms=13
mass=125
masssplitting=20

# to run sleptons.  make sure we set "-n" in the options below.
proc="isrslep"
params="SleptonBino"
charginofraction=""

while getopts "E:M:S:N:c:d:f:P:p:J:L:F:s:glab:Z:" opt; do
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
	b) database=$OPTARG;;
	Z) charginofraction=$OPTARG;;
	*) exit;;
    esac
done

clobberopts=""
if $clobber_mgpy; then
    clobberopts="-g -l -a"
elif $clobber_delphes; then
    clobberopts="-l -a"  # add -A to avoid rerunning madgraph+pythia
elif $clobber_ana; then
    clobberopts="-a"
fi

newmodelopts=""
if [[ $charginofraction != "" ]]; then
    charginomass=$(bc <<< "scale=0; ${mass}-${masssplitting}+${masssplitting}*${charginofraction}")
    newmodelopts="-v -O $charginomass"
fi

./run_VBFSUSY_standalone.sh \
    -E ${ecms} \
    -K ${kfactor} \
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
    -i -o \
    -y ${pythia_card} \
    -L ${delphes_card} \
    -f ${analysis} \
    -F ${likelihood} \
    -s ${suffix} \
    -n \
    -b ${database} \
    -I "madgraph-2.9.3" \
    ${newmodelopts} \
    ${clobberopts}
