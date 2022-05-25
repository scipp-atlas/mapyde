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
skip_PYHF=true
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
stopopts=""
gluinoopts=""
skip_pythia=false
kfactor=-1
chargino=-1

delphescard="delphes_card_ATLAS.tcl"
delphescardopt=""

# get command line options
while getopts "E:M:P:p:N:m:x:s:e:c:GDAglaB:b:j:J:S:y:k:d:C:iL:f:F:X:h:I:nvTruK:O:o" opt; do
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
	o) skip_PYHF=false;;
	L) delphescardopt=$OPTARG;;
	f) simpleanalysis=$OPTARG;;
	F) likelihood=$OPTARG;;
	X) xqcut=$OPTARG;;
	h) XSoverride=$OPTARG;;
	I) MGversion=$OPTARG;;
	n) sleptonopts="-s";;
	v) sleptonopts="-s -v";;
	T) skip_pythia=true;;
	K) kfactor=$OPTARG;;
	r)
	    proc=stops
	    params=StopBino
	    mmjj=0
	    deltaeta=0
	    pythia_card="pythia8_card.dat"
	    stopopts="-r";;
	u) 
	    proc=ttbar_and_gluino
	    params=GluinoBino
	    mmjj=0
	    deltaeta=0
	    pythia_card="pythia8_card.dat"
	    stopopts="-G";;
	O) chargino=$OPTARG;;
	    
	*) exit;;
    esac
done

# some modifications based on center of mass energy
lumi=1
if [[ $ecms == 13 ]]; then
    lumi=140000
    delphescard="delphes_card_ATLAS.tcl"
elif [[ $ecms == 14 ]]; then
    lumi=3000000
    delphescard="delphes_card_ATLAS.tcl"
elif [[ $ecms == 100 ]]; then
    lumi=3000000
    delphescard="FCChh.tcl"
fi

# but if we overrode the delphes card in the command line, then respect that.
if [[ $delphescardopt != "" ]]; then
    delphescard=$delphescardopt
fi


# construct the tag.
tag="VBFSUSY_${ecms}_${params}_${mass}_mmjj_${mmjj}_${mmjjmax}${suffix}"
if [[ $mmjj == 0.0 || $mmjj == 0 ]]; then
    if [[ $proc == "isrslep" && $chargino != -1 ]]; then
	tag="SUSY_${ecms}_${params}_${mass}_${dM}_${chargino}_${proc}_${suffix}"
	sleptonopts="${sleptonopts} -O ${chargino}"
    else
	tag="SUSY_${ecms}_${params}_${mass}_${dM}_${proc}_${suffix}"
    fi
fi

pythia_onoff=""
if $skip_pythia; then
    pythia_onoff="-T"
    echo "Skipping Pythia"
else
    echo "Not skipping Pythia"
fi

# run MadGraph+Pythia, using test script
if $skip_mgpy; then
    echo "Skipping Madgraph for this job."
else
    clobberopt=""
    if $clobber_mgpy; then
	clobberopt="-g"
    fi

    mgversionopt=""
    if [[ $MGversion != "" ]]; then
	mgversionopt="-I ${MGversion}"
    fi

    set -x
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
	${clobberopt} \
	${pythia_onoff} \
	${sleptonopts} \
	${stopopts} \
	${mgversionopt} \
	${tag}
    set +x
fi

# run Delphes, using test script
if $skip_delphes; then
    echo "Skipping delphes for this job."
else
    ./test/wrapper_delphes.sh ${tag} ${delphescard}  ${cores} ${clobber_delphes} ${database}
fi


XS=$(grep "Cross-section :" ${database}/${tag}/docker_mgpy.log | tail -1 | awk '{print $8}')
# if we're doing matching, then take a different value
if [[ $xqcut != -1 ]]; then
    XS=$(grep "cross-section :" ${database}/${tag}/docker_mgpy.log | tail -1 | awk '{print $9}')
fi

if [[ $kfactor != -1 ]]; then
    origXS=$(grep "Cross-section" ${database}/${tag}/docker_mgpy.log | tail -1 | awk '{print $8}')
    XSoverride=$(python3 -c "print(${kfactor}*${origXS})") # k-factor * LO XS
    echo "Changing cross section from $origXS to $XSoverride to account for k-factors"
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
    echo "Skipping SimpleAnalysis for this job."
else
    ./test/wrapper_ana.sh            ${tag} ${lumi} true ${database} "Delphes2SA.py" ${XS}
    ./test/wrapper_SimpleAnalysis.sh ${tag} ${lumi} ${database} ${simpleanalysis}
fi

if $skip_PYHF; then
    echo "Skipping likelihoods for this job."
else
    ./test/wrapper_pyhf.sh           ${tag} ${lumi} ${database} ${simpleanalysis} ${likelihood}
fi

