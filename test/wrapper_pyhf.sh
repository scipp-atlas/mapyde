#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
lumi=${2:-"1000"}
base=${PWD}
database=${3:-/data/users/${USER}/SUSY}
datadir=${tag}
analysis=${4:-EwkCompressed2018}
likelihood=${5:-Higgsino_2L_bkgonly}


# we'll need to run a script to take the contents of the SA ntuple and produce a JSON patch file
# that can go into pyhf along with a serialized likelihood for that analysis.
#
# will need to find a way to identify which bgkonly file to use, and to copy it into the /data
# area at the appropriate time (or access it elsewhere)
docker run \
       --log-driver=journald \
       --name "${tag}__SAtoJSON" \
       --rm \
       -v ${database}/${datadir}:/data \
       -v ${base}/scripts:/scripts \
       -v ${base}/likelihoods:/likelihoods \
       -w /data \
       gitlab-registry.cern.ch/scipp/mario-mapyde/pyplotting:master \
       "python /scripts/SAtoJSON.py -i ${analysis}.root -o ${analysis}_patch.json -n ${tag} -b /likelihoods/${likelihood}.json -l ${lumi}"


docker run \
       --log-driver=journald \
       --name "${tag}__pyhf" \
       --gpus all \
       --rm \
       -v ${database}/${datadir}:/data \
       -v ${base}/scripts:/scripts \
       -v ${base}/likelihoods:/likelihoods \
       -w /data \
       gitlab-registry.cern.ch/scipp/mario-mapyde/pyplotting:master \
       "python3 /scripts/likelihoodfitting.py -b /likelihoods/${likelihood}.json -s ${analysis}_patch.json -n ${tag}"
