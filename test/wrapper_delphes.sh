#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
delphescard=${2:-"delphes_card_ATLAS.tcl"}
cores=${3:-"1"}
clobber_delphes=${4:-"false"}
base=${PWD}
database=${5:-/data/users/${USER}/SUSY}
datadir=${tag}

# first check if delphes output is already there.  If so, then don't clobber it unless told to.
if [[ -e ${database}/${datadir}/delphes && $clobber_delphes != true ]]; then
    echo "Delphes area in ${datadir} already exists, not running job.  Remove or rename it, or force clobbering."
    exit 0
elif [[ -e ${database}/${datadir}/delphes && $clobber_delphes == true ]]; then
    dtst=$(date +%Y%m%d%H%M%S)
    echo "archiving previous delphes output as ${database}/${datadir}/delphes_${dtst} for later, just in case you want it again."
    cp -a ${database}/${datadir}/delphes ${database}/${datadir}/delphes_${dtst}
fi

set -x

#        --user $(id -u):$(id -g) \
docker run \
       --log-driver=journald \
       --name "${tag}__delphes" \
       --user $(id -u):$(id -g) \
       --rm \
       -v ${base}/cards:/cards \
       -v ${database}/${datadir}:/data \
       -w /tmp \
       --env delphescard=${delphescard} \
       ghcr.io/scipp-atlas/mario-mapyde/delphes:latest \
       'set -x && \
        cp $(find /data/ -name "*hepmc.gz") hepmc.gz && \
        gunzip hepmc.gz && \
	/bin/ls -ltrh --color && \
        /usr/local/share/delphes/delphes/DelphesHepMC2 /cards/delphes/${delphescard} delphes.root hepmc && \
        rsync -rav --exclude hepmc . /data/delphes'

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__delphes" > ${database}/${datadir}/docker_delphes.log

