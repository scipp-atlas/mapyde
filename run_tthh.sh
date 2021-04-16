#!/bin/bash
#set -e # exit when any command fails


export ATLAS_LOCAL_ROOT_BASE="/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase"
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
lsetup "python 3.8.8-x86_64-centos7"

#database=/data/users/mhance/tthh
database=/export/share/data/mhance/tthh
base=/export/home/mhance/mario-mapyde

# be careful of this, it will remove existing files if set to "clobber"
clobber_ana="false"
clobber_delphes="false"

lumi=3000000
delphescard="delphes_card_ATLAS_fixedbtageffic.tcl"

cores=1
docker=false
if [[ $HOSTNAME == slugpu* ]]; then
    cores=20
    docker=true
fi

proc=$1
ecms=$2
madgraphsherpa=$3
nevents=$4
tag=$5
seed=${6:-0}
seedoffset=${7:-0}

seed=$(($seed+$seedoffset))

datadir=${tag}/${seed}

echo "Executing run_tthh.sh with tag ${tag} seed $seed on machine $HOSTNAME"

if [[ $madgraphsherpa == "madgraph" ]]; then

    echo "-- running madgraph for ${proc}"
    params="sm"
    
    # ---------------------------------------------------------------------------------------
    # run madgraph+pythia
    #   -S cards/madspin/${proc} \
    ${base}/scripts/mg5creator.py \
	-o ${database} \
	-P ${base}/cards/process/${proc} \
	-r ${base}/cards/run/default_LO.dat \
	-p ${base}/cards/param/${params}.slha \
	-y ${base}/cards/pythia/pythia8_card.dat \
	-R ptb 20 -R ptj 20 -R etab 5.0 -R etaj 5.0 \
	-E "${ecms}000" \
	-c ${cores} \
	-n ${nevents} \
	-s ${seed} \
	-t ${tag}/${seed}

    # only run the job if the creation script succeeded, or if we're in batch mode and 
    if [[ $? == 0 ]]; then
	if $docker; then
	    docker run \
		--log-driver=journald \
		--name "${tag}__mgpy" \
		--rm \
		-v ${base}/cards:/cards \
		-v ${database}/${datadir}:/data \
		-w /output \
		gitlab-registry.cern.ch/scipp/mario-mapyde/madgraph:master \
		"mg5_aMC /data/run.mg5 && rsync -rav PROC_madgraph /data/${seed}/madgraph"
	    
  	    # dump docker logs to text file
	    journalctl -u docker CONTAINER_NAME="${tag}__mgpy" > $database/$datadir/docker_mgpy.log
	else
	    singularity exec \
		--contain \
		--no-home \
		--cleanenv \
		-B $PWD:/work \
		-B ${base}/cards:/cards \
		-B ${database}/${datadir}:/data \
		${base}/singularity/madgraph-2_7_3.sif \
		bash -c "df -h && cd /work && mg5_aMC /data/run.mg5 && rsync -rav --exclude Source --exclude lib --exclude bin PROC_madgraph /data/madgraph" \
		| tee $database/$datadir/docker_mgpy.log
	fi
    fi
    
else

    echo "-- running sherpa for ${proc}"
    ${base}/test/wrapper_sherpa.sh ${proc} ${ecms} ${nevents} ${tag} ${seed}
	
fi


# should not clobber existing output
echo "-- running delphes"
${base}/test/wrapper_delphes.sh ${tag} ${delphescard} 1 ${clobber_delphes} ${database} ${seed}
 
# should not clobber existing output
echo "-- running ana"
${base}/test/wrapper_ana.sh ${tag} ${lumi} ${clobber_ana} ${database} ${seed} "tthhAna.py"


pwd
ls -ltrh

#rm -rf *
