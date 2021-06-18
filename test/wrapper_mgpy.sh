#!/bin/bash
set -e # exit when any command fails

# defaults
ecms=100
mass=150
dM=5
proc=chargino
cores=20
nevents=1000
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
clobber_mgpy=false
clobber_delphes=false
clobber_ana=false
database=/data/users/${USER}/SUSY
ktdurham="-1"
xqcut="-1"
seed=0
pythia_card="cards/pythia/pythia8_card.dat"
base=${PWD}

while getopts "E:M:P:p:N:m:x:e:c:GgB:b:S:y:k:sd:j:J:X:" opt; do
    case "${opt}" in
	E) ecms=$OPTARG;;
	M) mass=$OPTARG;;
	P) proc=$OPTARG;;
	p) params=$OPTARG;;
	N) nevents=$OPTARG;;
	m) mmjj=$OPTARG;;
	x) mmjjmax=$OPTARG;;
	e) deltaeta=$OPTARG;;
	c) cores=$OPTARG;;
	g) clobber_mgpy=true;;
	B) base=$OPTARG;;
	b) database=$OPTARG;;
	j) ptj=$OPTARG;;
	J) ptj1min=$OPTARG;;
	S) dM=$OPTARG;;
	y) pythia_card=$OPTARG;;
	k) ktdurham=$OPTARG;;
	X) xqcut=$OPTARG;;
	s) slepton=true;;
	d) seed=$OPTARG;;
	\?) echo "Invalid option: -$OPTARG";;
    esac
done

shift $(($OPTIND - 1))
tag=${1:-"test_Higgsino_001"}
datadir=${tag}
mkdir -p ${database}

mN1=$(bc <<< "scale=2; ${mass}-${dM}")

if [[ ${slepton} == true ]]; then
    massopts="-m MSLEP ${mass}"
elif [[ ${params} == WinoBino ]]; then
    massopts="-m MN2 ${mass} -m MC1 ${mass}"
elif [[ ${params} == Higgsino ]]; then
    mC1=$(bc <<< "scale=2; ${mass}-${dM}/2")
    massopts="-m MN2 ${mass} -m MC1 ${mC1}"
fi

if [[ $xqcut != 0 && $xqcut != -1 ]]; then
    xqcuttmp="${xqcut} -R ickkw 1"
    xqcut=${xqcuttmp}
fi

./scripts/mg5creator.py \
    -o ${database} \
    -P cards/process/${proc} \
    -r cards/run/default_LO.dat \
    -p cards/param/${params}.slha \
    -y ${pythia_card} \
    -m MN1 ${mN1} ${massopts} \
    -R ptj ${ptj} -R ptj1min ${ptj1min} -R deltaeta ${deltaeta} -R mmjj ${mmjj} -R mmjjmax ${mmjjmax} -R ktdurham ${ktdurham} -R xqcut ${xqcut} \
    -c ${cores} \
    -E ${ecms}000 \
    -n ${nevents} \
    -s ${seed} \
    -t ${tag}

if [[ $? == 0 || ${clobber_mgpy} == true ]]; then
    docker run \
	   --log-driver=journald \
	   --name "${tag}__mgpy" \
	   --rm \
	   --user $(id -u):$(id -g) \
	   -v ${base}/cards:/cards \
	   -v ${database}/${datadir}:/data \
	   -w /tmp \
	   gitlab-registry.cern.ch/scipp/mario-mapyde/madgraph:master \
	   "mg5_aMC /data/run.mg5 && rsync -a PROC_madgraph /data/madgraph"
    
    # dump docker logs to text file
    journalctl -u docker CONTAINER_NAME="${tag}__mgpy" > ${database}/${datadir}/docker_mgpy.log
fi
