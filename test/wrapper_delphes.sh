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
       mhance/delphes:001 \
       'cp $(find /data/ -name "*hepmc.gz") hepmc.gz && \
        gunzip hepmc.gz && \
        /usr/local/share/delphes/delphes/DelphesHepMC /cards/delphes/delphes_card_ATLAS.tcl delphes.root hepmc && \
        rsync -rav --exclude hepmc . /data/delphes'

# to analyze delphes output
delphes_path="/usr/local/share/delphes/delphes"
docker run \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/scripts:/scripts \
       -v ${base}/${datadir}:/data \
       -w /output \
       --env DELPHES_PATH=${delphes_path} \
       mhance/delphes:001 \
       'export ROOT_INCLUDE_PATH=${ROOT_INCLUDE_PATH}:${DELPHES_PATH}:${DELPHES_PATH}/external && \
        /scripts/SimpleAna.py --input /data/delphes/delphes.root --output histograms.root && \
        rsync -rav . /data/analysis'
