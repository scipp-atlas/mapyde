#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
base=${PWD}
datadir=output/${tag}

docker run \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/${datadir}:/data \
       -w /output \
       gitlab-registry.cern.ch/scipp/mario-mapyde/delphes \
       'cp $(find /data/ -name "*hepmc.gz") hepmc.gz && \
        gunzip hepmc.gz && \
        /usr/local/share/delphes/delphes/DelphesHepMC /cards/delphes/delphes_card_ATLAS.tcl delphes.root hepmc && \
        rsync -rav --exclude hepmc . /data/delphes'

# to analyze delphes output
docker run \
       --name "${tag}__delphes" \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/scripts:/scripts \
       -v ${base}/${datadir}:/data \
       -w /output \
       gitlab-registry.cern.ch/scipp/mario-mapyde/delphes \
       '/scripts/SimpleAna.py --input /data/delphes/delphes.root --output histograms.root && \
        rsync -rav . /data/analysis'
