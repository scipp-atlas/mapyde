#!/bin/bash
set -e # exit when any command fails

proc=${1:-"tt"}
ecms=${2:-14}
events=${3:-"1000"}
tag=${4:-"test"}
seed=${5:-0}
base=/export/home/mhance/mario-mapyde
database=${6:-/export/share/diskvault3/mhance/tthh}

datadir=${tag}/${seed}

docker=false
if [[ $HOSTNAME == slugpu* ]]; then
    docker=true
fi

if [ -e ${base}/${datadir} ]; then
    echo "Output area ${datadir} already exists; choose a different name.  Aborting."
    exit
else
    mkdir -p ${database}/${datadir}/sherpa
    cp -p ${base}/cards/sherpa/${proc} ${database}/${datadir}/sherpa
fi

if $docker; then

    docker run \
	-it \
	--log-driver=journald \
	--name "${tag}__sherpa" \
	--rm \
	-v ${database}/${datadir}/sherpa:/output \
	-w /output \
	sherpamc/sherpa:2.2.7 \
	/bin/bash -c "Sherpa -f ${proc} -e ${events}"
    
        #/bin/bash -c "ls -ltrh && ls -ltrh /cards/sherpa/sherpa.tar && tar -xvf /cards/sherpa/sherpa.tar && Sherpa -f /cards/sherpa/${proc} -e ${events}"

    # dump docker logs to text file
    journalctl -u docker CONTAINER_NAME="${tag}__sherpa" > ${database}/${datadir}/docker_sherpa.log

else

    mkdir singularity_sandbox
    singularity exec \
	--contain \
	--no-home \
	--cleanenv \
	-B ${base}/gridpacks:/gridpacks \
	-B ${PWD}/singularity_sandbox:/work \
	-B ${database}/${datadir}/sherpa:/output \
	${base}/singularity/sherpa-2_2_7.sif \
	/bin/bash -c "cd /work && pwd && cp -p /gridpacks/${proc}.tar . && tar -xvf ${proc}.tar && ls -ltrh && Sherpa -f /output/${proc} -e ${events} -R ${seed} && ls -ltrh && cp -p sherpa.hepmc.hepmc2g /output && ls -ltrh /output" | tee ${database}/${datadir}/docker_sherpa.log
    rm -rf singularity_sandbox

fi

mv ${database}/${datadir}/sherpa/sherpa.hepmc.hepmc2g ${database}/${datadir}/sherpa/sherpa.hepmc.gz 
