#!/bin/bash
#set -e # exit when any command fails

database=/data/users/${USER}/SUSY

# be careful of this, it will remove existing files if set to "clobber"
clobber_ana=false
clobber_delphes=false
cores=12
anascript="SimpleAna.py"

seed=2

for EWKQCD in "EWK"; do
    for ecms in 100; do # omit 14 for re-running analysis
	max_mmjj_TeV=1
	mmjj_step=1
	mmjj_low=1
	if [[ $ecms == 100 ]]; then
	    max_mmjj_TeV=10
	    mmjj_step=20
	    mmjj_low=10
	fi
	for i_mmjj in $(seq ${mmjj_low} ${mmjj_step} ${max_mmjj_TeV}); do

            mmjj="${i_mmjj}000" # was 1 TeV for more inclusive sample
	    mmjjmax="$((mmjj+mmjj_step*1000))"
	    if [[ $i_mmjj == $max_mmjj_TeV ]]; then
		mmjjmax="-1"
	    fi

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

	    tag="Vjj${EWKQCD}_${ecms}_mmjj_${mmjj}_${mmjjmax}_${seed}"

	    base=${PWD}
	    datadir=${tag}

	    params="sm"

	    deltaeta=3.0
	    nevents=1000 # 1000000

	    # ---------------------------------------------------------------------------------------
	    # run madgraph+pythia
	    ./scripts/mg5creator.py \
		-o ${database} \
		-P cards/process/Vjj${EWKQCD} \
		-r cards/run/default_LO.dat \
		-p cards/param/${params}.slha \
		-y pythia8_card_dipoleRecoil.dat \
		-R mmjj ${mmjj} -R mmjjmax ${mmjjmax} -R deltaeta ${deltaeta}  -R mmll 40 \
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
           ghcr.io/scipp-atlas/mario-mapyde/madgraph:latest \
		       "mg5_aMC /data/run.mg5 && rsync -rav PROC_madgraph /data/madgraph  && chown -R $UID /data/madgraph"

		# dump docker logs to text file
		journalctl -u docker CONTAINER_NAME="${tag}__mgpy" > $database/$datadir/docker_mgpy.log
	    fi
	    # ---------------------------------------------------------------------------------------

	    # should not clobber existing output
	    ./test/wrapper_delphes.sh ${tag} ${delphescard} ${clobber_delphes}

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

	done
    done
done
