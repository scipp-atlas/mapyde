#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
lumi=${2:-"1000"}
clobber_ana=${3:-"false"}
base=/export/home/mhance/mario-mapyde
database=${4:-/data/users/${USER}/SUSY}
seed=${5:-0}
datadir=${tag}/${seed}
script=${6:-"SimpleAna.py"}


# first check if analysis output is already there.  If so, then don't clobber it unless told to.
if [[ -e ${database}/${datadir}/analysis && $clobber_ana != true ]]; then
    echo "Analysis area in ${datadir} already exists, not running job.  Remove or rename it, or force clobbering."
    exit 0
fi

docker=false
if [[ $HOSTNAME == slugpu* ]]; then
    docker=true
fi

set -x

# to analyze delphes output
if $docker; then
    docker run \
	--log-driver=journald \
	--name "${tag}__hists" \
	--rm \
	--user $(id -u):$(id -g) \
	-v ${base}/scripts:/scripts \
	-v ${database}/${datadir}:/data \
	-w /tmp \
	--env lumi=${lumi} \
	gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
	"set -x && \
        /scripts/${script} --input /data/delphes/delphes.root --output histograms.root --lumi ${lumi} && \
        rsync -rav . /data/analysis"
    
    # dump docker logs to text file
    journalctl -u docker CONTAINER_NAME="${tag}__hists" > ${database}/${datadir}/docker_ana.log
else
    singularity exec \
	--contain \
	--no-home \
	--cleanenv \
	-B ${PWD}:/work \
	-B ${base}/scripts:/scripts \
	-B ${database}/${datadir}:/data \
	--env lumi=${lumi} \
	docker://gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
	bash -c "set -x && cd /work && \
        /scripts/${script} --input /data/delphes/delphes.root --output histograms.root --lumi ${lumi} && \
        rsync -rav . /data/analysis && rm -rf *" | tee ${database}/${datadir}/docker_ana.log
fi
