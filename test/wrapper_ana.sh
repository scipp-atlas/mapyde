#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
lumi=${2:-"1000"}
clobber_ana=${3:-"false"}
base=${PWD}
database=${4:-/data/users/${USER}/SUSY}
datadir=${tag}
script=${5:-"SimpleAna.py"}
XS=${6:-0}

# first check if analysis output is already there.  If so, then don't clobber it unless told to.
if [[ -e ${database}/${datadir}/analysis && $clobber_ana != true ]]; then
    echo "Analysis area in ${datadir} already exists, not running job.  Remove or rename it, or force clobbering."
    exit 0
fi

outname=$(echo $script | sed s_"\.py"__g)

# to analyze delphes output
docker run \
       --log-driver=journald \
       --name "${tag}__hists" \
       --rm \
       --user $(id -u):$(id -g) \
       -v ${base}/cards:/cards \
       -v ${base}/scripts:/scripts \
       -v ${database}/${datadir}:/data \
       -w /tmp \
       --env lumi=${lumi} \
       ghcr.io/scipp-atlas/mario-mapyde/delphes:latest \
       "set -x && \
        /scripts/${script} --input /data/delphes/delphes.root --output ${outname}.root --lumi ${lumi} --XS ${XS} && \
        rsync -rav . /data/analysis"

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__hists" > ${database}/${datadir}/docker_ana.log
