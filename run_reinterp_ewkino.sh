#!/bin/bash
#set -e # exit when any command fails

nevents=50000
cores=8
seed=0
analysis="EwkCompressed2018"
likelihood="Higgsino_2L_bkgonly"
pythia_card="pythia8_card.dat"
delphes_card="delphes_card_ATLAS_lowptleptons.tcl"
ptj1min=100
deltaeta=0
mmjj=0.0
suffix="J${ptj1min}"
kfactor=1.3

clobber_mgpy=false
clobber_delphes=false
clobber_ana=false

ecms=13
mass=125
masssplitting=10

# to run sleptons.  make sure we set "-n" in the options below.
proc="isr2L"
params="Higgsino"

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
	*) exit;;
    esac
done
	

clobberopts=""
if $clobber_mgpy; then
    clobberopts="-g -l -a"
elif $clobber_delphes; then
    clobberopts="-l -a"
elif $clobber_ana; then
    clobberopts="-a"
fi


for thisproc in "${proc}nodecays" "${proc}"; do
    echo $thisproc

    skipopts=""
    XSoverride=""
    if [[ $thisproc == *nodecays ]]; then
	skipopts="-D -A -T" # don't run delphes or analysis or pythia or simpleanalysis for the nodecays case, there aren't enough useful events
	XSoverride=""
    else
	nodecayXS=$(grep "Cross-section" /data/users/${USER}/SUSY/SUSY_${ecms}_${params}_${mass}_${masssplitting}_${thisproc}nodecays_${suffix}/docker_mgpy.log | tail -1 | awk '{print $8}')
	XSoverride=$(python3 -c "print(${kfactor}*0.1*${nodecayXS})") # k-factor * BR * XS before BR
	skipopts="-i"
    fi

    set -x
    ./run_VBFSUSY_standalone.sh \
	-E ${ecms} \
	-M ${mass} \
	-P ${thisproc} \
	-c ${cores} \
	-m ${mmjj} \
	-e ${deltaeta} \
	-p ${params} \
	-S ${masssplitting} \
	-N ${nevents} \
	-d ${seed} \
	-J ${ptj1min} \
	-y ${pythia_card} \
	-L ${delphes_card} \
	-f ${analysis} \
	-F ${likelihood} \
	-h "${XSoverride}" \
	-s ${suffix} \
	-I "-2.9" \
	${skipopts} \
	${clobberopts}
    set +x
done
