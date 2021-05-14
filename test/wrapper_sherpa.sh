#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
proc=${2:-"tt"}
events=${3:-"1000"}
base=${PWD}
database=${4:-/data/users/${USER}/tthh}
datadir=${tag}

if [ -e ${base}/${datadir} ]; then
    echo "Output area ${datadir} already exists; choose a different name.  Aborting."
    exit
else
    mkdir -p ${database}/${datadir}/sherpa
    cp -p ${base}/cards/sherpa/${proc} ${database}/${datadir}/sherpa
fi

docker run \
       -it \
       --log-driver=journald \
       --name "${tag}__sherpa" \
       --rm \
       -v ${database}/${datadir}/sherpa:/output \
       -w /output \
       sherpamc/sherpa:2.2.7 \
       /bin/bash -c "mpirun -n 12 Sherpa -f ${proc} -e ${events}"

#       /bin/bash -c "ls -ltrh && ls -ltrh /cards/sherpa/sherpa.tar && tar -xvf /cards/sherpa/sherpa.tar && Sherpa -f /cards/sherpa/${proc} -e ${events}"

mv ${database}/${datadir}/sherpa/sherpa.hepmc.hepmc2g ${database}/${datadir}/sherpa/sherpa.hepmc.gz 

# dump docker logs to text file
journalctl -u docker CONTAINER_NAME="${tag}__sherpa" > ${database}/${datadir}/docker_sherpa.log
