#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
base=${PWD}
datadir=output/${tag}

if [ -e ${base}/${datadir} ]; then
    echo "Output area ${datadir} already exists; choose a different name.  Aborting."
    exit
else
    mkdir -p ${base}/${datadir}/sherpa
fi

docker run \
       -it \
       --log-driver=journald \
       --name "${tag}__sherpa" \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/${datadir}:/data \
       -v ${base}/${datadir}/sherpa:/output \
       -w /output \
       sherpamc/sherpa:2.2.7 \
       Sherpa -f /cards/sherpa/tt -e 1000

#       "ls /cards/sherpa/ && cp /cards/sherpa/tt ./Run.dat && Sherpa && ls -Rltrh"

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__sherpa" > $datadir/docker_sherpa.log


