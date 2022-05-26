#!/bin/bash
#set -e # exit when any command fails

# defaults
ecms=13
cores=20
nevents=100000
params=sm
mmjj=-1
mmjjmax=-1
deltaeta=-1
ptj=20
ptj1min=500
seed=123
database=/data/users/${USER}/boostedjets

for proc in 'Zbb' 'gluons' 'quarks'; do

    tag="${proc}"
    ./scripts/mg5creator.py \
	-o ${database} \
	-P cards/process/${proc} \
	-r cards/run/default_LO.dat \
	-p cards/param/${params}.slha \
	-E "${ecms}000" \
	-c ${cores} \
	-s ${seed} \
	-n ${nevents} \
	-t ${tag} \
	-R ptj1min ${ptj1min} 

    # only run the job if the creation script succeeded
    if [[ $? == 0 ]]; then
        docker run \
               --log-driver=journald \
               --name "${tag}__mgpy" \
               --rm \
               -v ${base}/cards:/cards \
               -v ${database}/${tag}:/data \
               -w /tmp \
               gitlab-registry.cern.ch/scipp/mario-mapyde/madgraph:master \
               "mg5_aMC /data/run.mg5 && rsync -rav PROC_madgraph /data/madgraph" #   && chown -R $UID /data/madgraph
        
        # dump docker logs to text file
        journalctl -u docker CONTAINER_NAME="${tag}__mgpy" > $database/$tag/docker_mgpy.log
    fi
    # ---------------------------------------------------------------------------------------

#               --user $(id -u):$(id -g) \
#               "wget http://madgraph.physics.illinois.edu/Downloads/models//heft.tgz && mv heft.tgz /usr/local/MG5_aMC_v2_7_3_py3/models && pushd /usr/local/MG5_aMC_v2_7_3_py3/models && tar -zxvf heft.tgz && popd && mg5_aMC /data/run.mg5 && rsync -rav PROC_madgraph /data/madgraph" #   && chown -R $UID /data/madgraph
    
done

