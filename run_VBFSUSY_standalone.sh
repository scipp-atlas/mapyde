#!/bin/bash
#set -e # exit when any command fails

# defaults
ecms=13
mass=150
dM=1
proc=VBFSUSY_EWKQCD
cores=20
nevents=10000
params=Higgsino
mmjj=500
mmjjmax=-1
deltaeta=3.0
ptj=20
ptj1min=0
suffix=""
skip_mgpy=false
skip_delphes=false
skip_ana=false
skip_SA=true
clobber_mgpy=false
clobber_delphes=false
clobber_ana=false
base=${PWD}
database=/data/users/${USER}/SUSY
datadir=${tag}
ktdurham=-1
xqcut=-1
seed=0
pythia_card="pythia8_card_dipoleRecoil.dat"
anascript="SimpleAna.py"
simpleanalysis="EwkCompressed2018"
likelihood="Higgsino_2L_bkgonly"
XSoverride=""
MGversion=""
sleptonopts=""
skip_pythia=false

# some modifications based on run parameters
lumi=1
if [[ $ecms == 13 ]]; then
    if [ "$mass" -ge "1000" ]; then
	exit
    fi
    lumi=140000
    delphescard="delphes_card_ATLAS.tcl"
elif [[ $ecms == 14 ]]; then
    if [ "$mass" -ge "1000" ]; then
	exit
    fi
    lumi=3000000
    delphescard="delphes_card_ATLAS.tcl"
elif [[ $ecms == 100 ]]; then
    if [ "$mass" -le "200" ]; then
	exit
    fi
    lumi=3000000
    delphescard="FCChh.tcl"
fi


# get command line options
while getopts "E:M:P:p:N:m:x:s:e:c:GDAglaB:b:j:J:S:y:k:d:C:iL:f:F:X:h:I:nvT" opt; do
    case "${opt}" in
	E) ecms=$OPTARG;;
	M) mass=$OPTARG;;
	P) proc=$OPTARG;;
	p) params=$OPTARG;;
	N) nevents=$OPTARG;;
	m) mmjj=$OPTARG;;
	x) mmjjmax=$OPTARG;;
	s) suffix=$OPTARG;;
	e) deltaeta=$OPTARG;;
	c) cores=$OPTARG;;
	G) skip_mgpy=true;;
	D) skip_delphes=true;;
	A) skip_ana=true;;
	g) clobber_mgpy=true;;
	l) clobber_delphes=true;;
	a) clobber_ana=true;;
	B) base=$OPTARG;;
	b) database=$OPTARG;;
	j) ptj=$OPTARG;;
	J) ptj1min=$OPTARG;;
	S) dM=$OPTARG;;
	y) pythia_card=$OPTARG;;
	k) ktdurham=$OPTARG;;
	d) seed=$OPTARG;;
	C) anascript=$OPTARG;;
	i) skip_SA=false;;
	L) delphescard=$OPTARG;;
	f) simpleanalysis=$OPTARG;;
	F) likelihood=$OPTARG;;
	X) xqcut=$OPTARG;;
	h) XSoverride=$OPTARG;;
	I) MGversion=$OPTARG;;
	n) sleptonopts="-s";;
	v) sleptonopts="-s -v";;
	T) skip_pythia=true;;
	r) 
	    proc=stops
	    param=StopBino
	    mmjj=0
	    deltaeta=0
	    pythia_card="pythia8_card.dat";;
	*) exit;;
    esac
done

# construct the tag.
tag="VBFSUSY_${ecms}_${params}_${mass}_mmjj_${mmjj}_${mmjjmax}${suffix}"
if [[ $mmjj == 0.0 ]]; then
   tag="SUSY_${ecms}_${params}_${mass}_${dM}_${proc}_${suffix}"
fi

pythia_onoff=""
if $skip_pythia; then
    pythia_onoff="-T"
fi

# run MadGraph+Pythia, using test script
if $skip_mgpy; then
    echo "Skipping Madgraph for this job."
else
    clobberopt=""
    if $clobber_mgpy; then
	clobberopt="-g"
    fi

    ./test/wrapper_mgpy.sh \
	-b ${database} \
	-P ${proc} \
	-p ${params} \
	-y ${pythia_card} \
	-S ${dM} \
	-M ${mass} \
	-m ${mmjj} \
	-x ${mmjjmax} \
	-e ${deltaeta} \
	-E ${ecms} \
	-c ${cores} \
	-k ${ktdurham} \
	-X ${xqcut} \
	-N ${nevents} \
	-d ${seed} \
	-j ${ptj} \
	-J ${ptj1min} \
	-I "${MGversion}" \
	${clobberopt} \
	${pythia_onoff} \
	${sleptonopts} \
	${tag}
fi

# run Delphes, using test script
if $skip_delphes; then
    echo "Skipping delphes for this job."
else
    ./test/wrapper_delphes.sh ${tag} ${delphescard}  ${cores} ${clobber_delphes}
fi


XS=$(grep "Cross-section :" ${database}/${tag}/docker_mgpy.log | tail -1 | awk '{print $8}')
# if we're doing matching, then take a different value
if [[ $xqcut != -1 ]]; then
    XS=$(grep "cross-section :" ${database}/${tag}/docker_mgpy.log | tail -1 | awk '{print $9}')
fi

if [[ $XSoverride != "" ]]; then
    echo "Using Cross Section = $XSoverride instead of $XS"
    XS=$XSoverride
fi

# run ntuplizing, using test script
if $skip_ana; then
    echo "Skipping ana for this job."
else
    ./test/wrapper_ana.sh ${tag} ${lumi} ${clobber_ana} ${database} ${anascript} ${XS}
fi

# run SimpleAnalysis + likelihoods.  not usual.
if $skip_SA; then
    echo "Skipping SimpleAnalysis+likelihoods for this job."
else
    ./test/wrapper_ana.sh            ${tag} ${lumi} true ${database} "Delphes2SA.py" ${XS}
    ./test/wrapper_SimpleAnalysis.sh ${tag} ${lumi} ${database} ${simpleanalysis}
    ./test/wrapper_pyhf.sh           ${tag} ${lumi} ${database} ${simpleanalysis} ${likelihood}
fi

