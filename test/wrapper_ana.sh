#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
lumi=${2:-"1000"}
base=${PWD}
datadir=output/${tag}

set -x

# to analyze delphes output
docker run \
       --log-driver=journald \
       --name "${tag}__hists" \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/scripts:/scripts \
       -v ${base}/${datadir}:/data \
       -w /output \
       --env lumi=${lumi} \
       gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
       'set -x && \
        /scripts/SimpleAna.py --input /data/delphes/delphes.root --output histograms.root --lumi ${lumi} && \
        rsync -rav . /data/analysis'

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__hists" > $datadir/docker_ana.log
