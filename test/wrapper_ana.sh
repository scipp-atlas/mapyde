#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
lumi=${2:-"1000"}
clobber_ana=${3:-"false"}
base=${PWD}
database=/data/users/mhance/SUSY
datadir=${tag}

# first check if analysis output is already there.  If so, then don't clobber it unless told to.
if [[ -e ${database}/${datadir}/analysis && $clobber_ana != true ]]; then
    echo "Analysis area in ${datadir} already exists, not running job.  Remove or rename it, or force clobbering."
    exit 0
fi

set -x

# to analyze delphes output
docker run \
       --log-driver=journald \
       --name "${tag}__hists" \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/scripts:/scripts \
       -v ${database}/${datadir}:/data \
       -w /output \
       --env lumi=${lumi} \
       gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
       'set -x && \
        /scripts/SimpleAna.py --input /data/delphes/delphes.root --output histograms.root --lumi ${lumi} && \
        rsync -rav . /data/analysis'

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__hists" > ${database}/${datadir}/docker_ana.log
