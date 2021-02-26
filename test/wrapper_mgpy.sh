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
suffix=""
skip_mgpy=false
skip_delphes=false
skip_ana=false
clobber_mgpy=false
clobber_delphes=false
clobber_ana=false
database=/data/users/${USER}/SUSY
ktdurham="-1"
seed=0
pythia_card="cards/pythia/pythia8_card.dat"
base=${PWD}

while getopts "E:M:P:p:N:m:x:e:c:GgB:b:S:y:k:s" opt; do
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
	S) dM=$OPTARG;;
	y) pythia_card=$OPTARG;;
	k) ktdurham=$OPTARG;;
	s) slepton=true;;
	d) seed=$OPTARG;;
	\?) echo "Invalid option: -$OPTARG";;
    esac
done

shift $(($OPTIND - 1))
tag=${1:-"test_Higgsino_001"}
datadir=${tag}

mN1=$(bc <<< "scale=2; ${mass}-${dM}")

if [[ ${slepton} == true ]]; then
    massopts="-m MSLEP ${mass}"
else
    massopts="-m MN2 ${mass} -m MC1 ${mass}"
fi

./scripts/mg5creator.py \
    -o ${database} \
    -P cards/process/${proc} \
    -r cards/run/default_LO.dat \
    -p cards/param/${params}.slha \
    -y ${pythia_card} \
    -m MN1 ${mN1} ${massopts} \
    -R ptj ${ptj} -R deltaeta ${deltaeta} -R mmjj ${mmjj} -R mmjjmax ${mmjjmax} -R ktdurham ${ktdurham} \
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
	   -v ${base}/cards:/cards \
	   -v ${database}/${datadir}:/data \
	   -w /output \
	   gitlab-registry.cern.ch/scipp/mario-mapyde/madgraph:master \
	   "mg5_aMC /data/run.mg5 && rsync -rav PROC_madgraph /data/madgraph"
    
    # dump docker logs to text file
    journalctl -u docker CONTAINER_NAME="${tag}__mgpy" > ${database}/${datadir}/docker_mgpy.log
fi
