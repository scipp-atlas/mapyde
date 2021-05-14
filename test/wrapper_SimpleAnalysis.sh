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
       -v ${database}/${datadir}:/data \
       -w /data \
       gitlab-registry.cern.ch/atlas-sa/simple-analysis \
       -a ${analysis} \
       analysis/histograms.root -n

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__SimpleAnalysis" > ${database}/${datadir}/docker_SimpleAnalysis.log

# the above command will create a ROOT file with an ntuple inside, creatively called "ntuple".
# we'll need to run a script to take the contents of that ntuple and produce a JSON patch file
# that can go into pyhf along with a serialized likelihood for that analysis.
#
# will need to find a way to identify which bgkonly file to use, and to copy it into the /data
# area at the appropriate time (or access it elsewhere)
docker run \
       --log-driver=journald \
       --name "${tag}__SAtoJSON" \
       --rm \
       --entrypoint bash \
       -v ${database}/${datadir}:/data \
       -v ${base}/scripts:/scripts \
       -w /data \
       pyhf/pyhf \
       "/scripts/SAtoJSON.py -i ${analysis}.root -o ${analysis}_patch.json -n ${tag} -b Higgsino_2L_bkgonly.json"
