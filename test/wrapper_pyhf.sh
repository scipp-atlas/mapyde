#!/bin/bash
#set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
lumi=${2:-"1000"}
base=${PWD}
database=${3:-/data/users/${USER}/SUSY}
datadir=${tag}
analysis=${4:-EwkCompressed2018}
likelihood=${5:-Higgsino_2L_bkgonly}


# --------------------------------------------------------------------------------------------------
# we'll need to run a script to take the contents of the SA ntuple and produce a JSON patch file
# that can go into pyhf along with a serialized likelihood for that analysis.
#
# will need to find a way to identify which bgkonly file to use, and to copy it into the /data
# area at the appropriate time (or access it elsewhere)
docker run \
       --log-driver=journald \
       --name "${tag}__SAtoJSON" \
       --rm \
       --user $(id -u):$(id -g) \
       -v ${database}/${datadir}:/data \
       -v ${base}/scripts:/scripts \
       -v ${base}/likelihoods:/likelihoods \
       -w /data \
       ghcr.io/scipp-atlas/mario-mapyde/pyplotting:latest \
       "python /scripts/SAtoJSON.py -i ${analysis}.root -o ${analysis}_patch.json -n ${tag} -b /likelihoods/${likelihood}.json -l ${lumi}"

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__SAtoJSON" > ${database}/${datadir}/docker_SAtoJSON.log
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# run a simple mu scan.  this can be faster, just using pyhf.
#
GPUopts="-c"
if [[ $(hostname) == "slugpu" ]]; then
    GPUopts=""
fi

docker run \
       --log-driver=journald \
       --name "${USER}_${tag}__muscan" \
       --gpus all \
       --rm \
       --user $(id -u):$(id -g) \
       -v ${database}/${datadir}:/data \
       -v ${base}/scripts:/scripts \
       -v ${base}/likelihoods:/likelihoods \
       -w /data \
       ghcr.io/scipp-atlas/mario-mapyde/pyplotting-cuda:latest \
       "time python3.8 /scripts/muscan.py -b /likelihoods/${likelihood}.json -s ${analysis}_patch.json -n ${tag} ${GPUopts}"

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${USER}_${tag}__muscan" > ${database}/${datadir}/docker_muscan.log
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# do everything in cabinetry instead.
#
# docker run \
#        --log-driver=journald \
#        --name "${tag}__cabinetry" \
#        --gpus all \
#        --rm \
#        -v ${database}/${datadir}:/data \
#        -v ${base}/scripts:/scripts \
#        -v ${base}/likelihoods:/likelihoods \
#        -w /data \
#        ghcr.io/scipp-atlas/mario-mapyde/pyplotting-cuda:latest \
#        "python3.8 /scripts/likelihoodfitting.py -b /likelihoods/${likelihood}.json -s ${analysis}_patch.json -n ${tag}"

# # dump docker logs to text file
# journalctl -u docker CONTAINER_NAME="${tag}__cabinetry" > ${database}/${datadir}/docker_cabinetry.log
# --------------------------------------------------------------------------------------------------
