#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
delphescard=${2:-"delphes_card_ATLAS.tcl"}
cores=${3:-"1"}
clobber_delphes=${4:-"false"}
base=/export/home/mhance/mario-mapyde
database=${5:-/data/users/${USER}/SUSY}
seed=${6:-0}
datadir=${tag}/${seed}

# first check if delphes output is already there.  If so, then don't clobber it unless told to.
if [[ -e ${database}/${datadir}/delphes && $clobber_delphes != true ]]; then
    echo "Delphes area in ${datadir} already exists, not running job.  Remove or rename it, or force clobbering."
    exit 0
fi

docker=false
if [[ $HOSTNAME == slugpu* ]]; then
    docker=true
fi

if $docker; then
    docker run \
	--log-driver=journald \
	--name "${tag}__delphes" \
	--user $(id -u):$(id -g) \
	--rm \
	-v ${base}/cards:/cards \
	-v ${database}/${datadir}:/data \
	-w /tmp \
	--env delphescard=${delphescard} \
	gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
	'set -x && \
        cp $(find /data/ -name "*hepmc.gz") hepmc.gz && \
        gunzip hepmc.gz && \
	/bin/ls -ltrh --color && \
        /usr/local/share/delphes/delphes/DelphesHepMC /cards/delphes/${delphescard} delphes.root hepmc && \
        rsync -rav --exclude hepmc . /data/delphes'

    # dump docker logs to text file
    journalctl -u docker CONTAINER_NAME="${tag}__delphes" > ${database}/${datadir}/docker_delphes.log

else
    singularity exec \
	--contain \
	--no-home \
	--cleanenv \
	-B ${PWD}:/work \
	-B ${base}/cards:/cards \
	-B ${database}/${datadir}:/data \
	--env delphescard=${delphescard} \
	docker://gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
	bash -c 'cd /work && set -x && \
        cp $(find /data/ -name "*hepmc.gz") hepmc.gz && \
        gunzip hepmc.gz && \
	/bin/ls -ltrh --color && \
        /usr/local/share/delphes/delphes/DelphesHepMC /cards/delphes/${delphescard} delphes.root hepmc && \
        rsync -rav --exclude hepmc . /data/delphes && rm -rf *'  | tee ${database}/${datadir}/docker_delphes.log
fi


