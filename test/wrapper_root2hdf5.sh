#!/bin/bash
#set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
base=${PWD}
database=${3:-/data/users/${USER}/SUSY}
datadir=${tag}

# --------------------------------------------------------------------------------------------------
docker run \
       --log-driver=journald \
       --name "${tag}__root2hdf5" \
       --rm \
       --user $(id -u):$(id -g) \
       -v ${database}/${datadir}:/data \
       -v ${base}/scripts:/scripts \
       -v ${base}/likelihoods:/likelihoods \
       -w /data \
       ghcr.io/scipp-atlas/mario-mapyde/pyplotting:latest \
       "python3 /scripts/root2hdf5.py analysis/lowlevelAna.root:allev/lowleveltree"

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__root2hdf5" > ${database}/${datadir}/docker_root2hdf5.log
# --------------------------------------------------------------------------------------------------

