#!/bin/bash
#set -e # exit when any command fails

database=/data/users/${USER}/SUSY

# be careful of this, it will remove existing files if set to "clobber"
clobber_ana=true
clobber_delphes=false
cores=12
anascript="lowlevelAna.py"
mmjj=0
mmjjmax=-1
seed=2
params="sm"
deltaeta=-1
nevents=10000


for ecms in 13; do
    
    if [[ $ecms == 13 ]]; then
	lumi=140000
	delphescard="delphes_card_ATLAS.tcl"
    elif [[ $ecms == 14 ]]; then
	lumi=3000000
	delphescard="delphes_card_ATLAS.tcl"
    elif [[ $ecms == 100 ]]; then
	lumi=3000000
	delphescard="FCChh.tcl"
    fi
    
    tag="ttbar_${ecms}_${seed}"
	
    base=${PWD}
    datadir=${tag}
    
    # ---------------------------------------------------------------------------------------
    # run madgraph+pythia
    ./scripts/mg5creator.py \
	-o ${database} \
	-P cards/process/ttbar \
	-r cards/run/default_LO.dat \
	-p cards/param/${params}.slha \
	-E "${ecms}000" \
	-c ${cores} \
	-s ${seed} \
	-n ${nevents} \
	-t ${tag}
	
    # only run the job if the creation script succeeded
    if [[ $? == 0 ]]; then
	docker run \
	       --log-driver=journald \
	       --name "${tag}__mgpy" \
	       --rm \
	       --user $(id -u):$(id -g) \
	       -v ${base}/cards:/cards \
	       -v ${database}/${datadir}:/data \
	       -w /tmp \
	       gitlab-registry.cern.ch/scipp/mario-mapyde/madgraph:master \
	       "mg5_aMC /data/run.mg5 && rsync -rav PROC_madgraph /data/madgraph" #   && chown -R $UID /data/madgraph
	
	# dump docker logs to text file
	journalctl -u docker CONTAINER_NAME="${tag}__mgpy" > $database/$datadir/docker_mgpy.log
    fi
    # ---------------------------------------------------------------------------------------
	
    # should not clobber existing output
    #./test/wrapper_delphes.sh ${tag} ${delphescard} ${clobber_delphes}

    # should not clobber existing output
    XS=$(grep "Cross-section :" ${database}/${tag}/docker_mgpy.log | tail -1 | awk '{print $8}')
    echo "tag=$tag"
    echo "lumi=$lumi"
    echo "clobber=$clobber_ana"
    echo "database=$database"
    echo "script=$anascript"
    echo "XS=$XS"
    set -x
    ./test/wrapper_ana.sh ${tag} ${lumi} ${clobber_ana} ${database} ${anascript} ${XS}
    set +x

    #./test/wrapper_root2hdf5.sh ${tag}
    python3 scripts/root2hdf5.py /data/users/mhance/SUSY/${tag}/analysis/lowlevelAna.root:allev/lowleveltree
   
done
