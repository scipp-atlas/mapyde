#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
base=${PWD}
datadir=output/${tag}

docker run \
       --log-driver=journald \
       --name "${tag}__delphes" \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/${datadir}:/data \
       -w /output \
       gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
       'cp $(find /data/ -name "*hepmc.gz") hepmc.gz && \
        gunzip hepmc.gz && \
        /usr/local/share/delphes/delphes/DelphesHepMC /cards/delphes/delphes_card_ATLAS.tcl delphes.root hepmc && \
        rsync -rav --exclude hepmc . /data/delphes'

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__delphes" > $datadir/docker_delphes.log

# to analyze delphes output
docker run \
       --log-driver=journald \
       --name "${tag}__hists" \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/scripts:/scripts \
       -v ${base}/${datadir}:/data \
       -w /output \
       gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
       '/scripts/SimpleAna.py --input /data/delphes/delphes.root --output histograms.root && \
        rsync -rav . /data/analysis'

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__hists" > $datadir/docker_hists.log
