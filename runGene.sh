#!/bin/bash

### Arguements
### 1) Binary 2) Process 3) Param 4) Run Card 5) Delphes Card 6) process number

echo "================================================================"
echo "=========================== WELCOME! ==========================="
hostname
echo $HOSTNAME
pwd
whoami
/bin/ls -ltrh
echo $@
echo "================================================================"
echo "================================================================"
echo "Setting up the environment (mostly empty for now)"
bin=${1}
process=${2}
param=${3}
run=${4}
delphes=${5}
jobNo=${6}
# Print config
echo -e "\tJob Number:   ${jobNo}"
echo -e "\tBin:          ${bin}"
echo -e "\tGene Process: ${process}"
echo -e "\tParam Card:   ${param}"
echo -e "\tRun Card:     ${run}"
echo -e "\tDelphes Card: ${delphes}"

### Re-construct the job name
runC=${run##*/}
runC=${runC%.*}
#
processC=${process##*/}
processC=${processC%.*}
#
paramC=${param##*/}
paramC=${paramC%.*}
#
delphesC=${delphes##*/}
delphesC=${delphesC%.*}
#
jobName="${processC}_${paramC}_${runC}_${delphesC}.${jobNo}"
echo "Labeling job as $jobName"
cp $process $processC
# Dummy PROC name so that I can find it later
dummyName="PROC_HAZ"

### Make the MG5 job configuration and print it
echo "================================================================"
echo "================================================================"
echo "Preparing MG job script"
jobScript=${PWD}/mg5Job.${jobNo}.mg5
cat ${processC} > ${jobScript}
echo "output ${dummyName}" >> ${jobScript}
hn=$(hostname)
if [[ $hn == atlas02.ucsc.edu ]]; then
    echo "set run_mode 2" >> ${jobScript}
    echo "set nb_core 12" >> ${jobScript}
else
    echo "set run_mode 0" >> ${jobScript}
fi
echo "launch ${dummyName}" >> ${jobScript}
if [[ $process == *NLO* ]]; then
    echo "shower=PYTHIA8" >> ${jobScript}
fi
if [[ $process == *_MS ]]; then
    echo "madspin=ON" >> ${jobScript}
    if [[ $process == *_MS ]]; then
	if [[ $process == *test* ]]; then
	    echo "decay z > f f" >> ${jobScript}
	elif [[ $process == *tH* ]]; then
	    echo "decay t~ > w- b~, w- > f f" >> ${jobScript}
	    echo "decay t  > w+ b , w+ > f f" >> ${jobScript}
	    echo "decay h+ >  w+ h1, h1 > ta+ ta-, w+ > f f" >> ${jobScript}
	    echo "decay h- >  w- h1, h1 > ta+ ta-, w- > f f" >> ${jobScript}
	elif [[ $process == *HWbb* ]]; then
	    echo "decay w+ > f f" >> ${jobScript}
	    echo "decay w- > f f" >> ${jobScript}
	elif [[ $proces == *hH* ]]; then
	    # no advantage to decaying h1 here, it's a scalar, let Pythia do it.
	    echo "decay h+ >  w+ h1, w+ > l+ vl" >> ${jobScript}
	    echo "decay h- >  w- h1, w- > l- vl~" >> ${jobScript}
	fi
    fi
else
    echo "madspin=OFF" >> ${jobScript}
fi    
if [[ $process != *NLO* ]]; then
    echo "shower=Pythia8" >> ${jobScript}
fi
if [[ $process != *NLO* ]]; then
    echo "detector=Delphes" >> ${jobScript}
fi
if [ ${param} != "SM" ]; then
    echo ${param} >> ${jobScript}
fi
echo ${run} >> ${jobScript}
echo "set iseed $((1223*(1+jobNo)))" >> ${jobScript}
if [[ $process == *_PY ]]; then
    if [[ $process == *tH* ]]; then
	echo "/export/share/diskvault2/mhance/PhenoPaper2018/Submit/PythiaCards/pythia8_card_h1tautau.dat" >> ${jobScript}
    fi
fi
if [[ $process != *NLO* ]]; then
    echo ${delphes} >> ${jobScript}
else
    echo "done" >> ${jobScript}
fi
echo "" >> ${jobScript}
echo ">>>"
cat ${jobScript}
echo ">>>"

### DO IT!
echo "================================================================"
echo "================================================================"
echo "Running MG5 with commands:"
cat ${jobScript}
echo "Running: ${bin} ${jobScript}"
${bin} ${jobScript}
echo ">>>> DONE!  Directory Contents:"
/bin/ls -ltrh

### Run Delphes by hand if in NLO mode
if [[ $process == *NLO* ]]; then
    echo "================================================================"
    echo "================================================================"
    echo "Running Delphes"
    
    cp -p ${dummyName}/Events/*/events_PYTHIA8_0.hepmc.gz .
    gunzip events_PYTHIA8_0.hepmc.gz
    /export/share/diskvault2/mhance/PhenoPaper2018/Generate/Delphes-3.4.1/DelphesHepMC ${delphes} delphes_events.${jobNo}.root events_PYTHIA8_0.hepmc
    rm events_PYTHIA8_0.hepmc
fi

### Still todo really
echo "================================================================"
echo "================================================================"
echo "Post Processing"
# Extract the LHE files, etc (wildcard the run dir, just in case)
echo "Moving event outputs..."
if [[ $process != *NLO* ]]; then
    mv -v ${dummyName}/Events/*/unweighted_events.lhe.gz      ./events.${jobNo}.lhe.gz
    mv -v ${dummyName}/Events/*/tag_1_pythia8_events.hepmc.gz ./pythia8_events.${jobNo}.hepmc.gz
    mv -v ${dummyName}/Events/*/tag_1_delphes_events.root     ./delphes_events.${jobNo}.root
else
    if [[ $process == *_MS ]]; then
	mv -v ${dummyName}/Events/run_01_decayed_1/events.lhe.gz  ./events.${jobNo}.lhe.gz
    else
	mv -v ${dummyName}/Events/run_01/events.lhe.gz            ./events.${jobNo}.lhe.gz
    fi
    mv -v ${dummyName}/Events/*/events_PYTHIA8_0.hepmc.gz     ./pythia8_events.${jobNo}.hepmc.gz
fi    

# move the gridpack, if it's there
cp -p PROC_HAZ/run_01_gridpack.tar.gz .


# now, if we're making histograms, do it here:
source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
source /export/share/diskvault2/mhance/PhenoPaper2018/Ana/setupEnv.sh
/export/share/diskvault2/mhance/PhenoPaper2018/Ana/SimpleAna.py \
    --input ./delphes_events.${jobNo}.root \
    --output hist.${jobName}.root

# tar/zip the remains in the PROC dir
echo "Tar'ing the PROC directory..."
tar czvf ${jobName}.tar.gz ${dummyName}
echo "Final snapshot of workdir:"
/bin/ls -ltrh
echo "================================================================"
echo "================================================================"
echo "DONE! GOODBYE"
