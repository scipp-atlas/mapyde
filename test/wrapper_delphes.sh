#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
delphescard=${2:-"delphes_card_ATLAS.tcl"}
cores=${3:-"1"}
base=${PWD}
datadir=output/${tag}

set -x

docker run \
       --log-driver=journald \
       --name "${tag}__delphes" \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/${datadir}:/data \
       -w /output \
       --env delphescard=${delphescard} \
       gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
       'set -x && \
        cp $(find /data/ -name "*hepmc.gz") hepmc.gz && \
        gunzip hepmc.gz && \
	/bin/ls -ltrh --color && \
        /usr/local/share/delphes/delphes/DelphesHepMC /cards/delphes/${delphescard} delphes.root hepmc && \
        rsync -rav --exclude hepmc . /data/delphes'

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__delphes" > $datadir/docker_delphes.log

