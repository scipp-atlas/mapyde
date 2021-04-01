#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
lumi=${2:-"1000"}
clobber_ana=${3:-"false"}
base=${PWD}
database=${4:-/data/users/${USER}/SUSY}
datadir=${tag}

# first check if analysis output is already there.  If so, then don't clobber it unless told to.
if [[ -e ${database}/${datadir}/analysis && $clobber_ana != true ]]; then
    echo "Analysis area in ${datadir} already exists, not running job.  Remove or rename it, or force clobbering."
    exit 0
fi

set -x

docker run \
       --log-driver=journald \
       --name "${tag}__SimpleAnalysis" \
       --rm \
       -v ${database}/${datadir}:/data \
       -w /data \
       gitlab-registry.cern.ch/atlas-sa/simple-analysis \
       -a EwkCompressed2018 \
       analysis/histograms.root

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__SimpleAnalysis" > ${database}/${datadir}/docker_SimpleAnalysis.log
