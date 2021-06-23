#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
lumi=${2:-"1000"}
base=${PWD}
database=${3:-/data/users/${USER}/SUSY}
datadir=${tag}
analysis=${4:-EwkCompressed2018}

docker run \
       --log-driver=journald \
       --name "${tag}__SimpleAnalysis" \
       --rm \
       --user $(id -u):$(id -g) \
       -v ${database}/${datadir}:/data \
       -w /data \
       gitlab-registry.cern.ch/atlas-phys-susy-wg/simpleanalysis:master \
       -a ${analysis} \
       analysis/Delphes2SA.root -n

# # dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__SimpleAnalysis" > ${database}/${datadir}/docker_SimpleAnalysis.log

#       gitlab-registry.cern.ch/atlas-sa/simple-analysis \
