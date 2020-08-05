### Makes a submission file for mg5 generation to condor
###
### Arguements: 1) process, 2) param card, 3) run card 4) Delphes Card 5) Optional, job multiplier
### Arguements will have "."-endings stripped
###  -- so don't put useful bookkeeping information there!
### All environment variables taken from submitting shell (so setup ROOT!)

### Basics
STAMP="BkgProd_v2"
if [[ $6 != "" ]]; then
    STAMP=$6
fi

exe="runGene.sh"
mg5BinPath=/export/share/diskvault2/mhance/PhenoPaper2018/Generate/MG5_aMC_v2_6_4/bin/mg5_aMC # was 6_1
gridpackinput=""
fullOutput=1
if [[ ${7} == "gridpack" ]]; then
    gridpackinput=$7
    exe="runGeneGridpack.sh"
    mg5BinPath="./run.sh"
elif [[ ${7} == "reduced" ]]; then
    fullOutput=0
fi

### Make all paths absolute if not already
process=`echo $PWD/${1}` # was readlink, but want to keep link names intact
run=`readlink -f ${3}`
delphes=`readlink -f ${4}`
gridpackinput=`readlink -f ${gridpackinput}`
param=${2}
if [ ${2} != "SM" ]; then
    param=`readlink -f ${2}`
fi

### Cleanup inputs for book keeping purposes
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
gridpackC=${gridpackinput##*/}
gridpackC=${gridpackinput%.*}

echo $gridpackC

jobName=${processC}_${paramC}_${runC}_${delphesC}

### Set outputs, and condor cfg
outputDir=${PWD}/${STAMP}/${jobName}
subfile=${outputDir}/condorEvgen.cfg

# Check for gridpack run
gp=$(grep -i gridpack $run | egrep -v "False")
if [[ $gp != "" ]]; then
    gridpackoutput="run_01_gridpack.tar.gz"
    gridpackremap="run_01_gridpack.tar.gz = ${outputDir}/gridpack.\$(Process).tar.gz"
else
    gridpackoutput="events.\$(Process).lhe.gz,delphes_events.\$(Process).root" # pythia8_events.\$(Process).hepmc.gz,
    gridpackremap="events.\$(Process).lhe.gz = ${outputDir}/events.\$(Process).lhe.gz ; delphes_events.\$(Process).root = ${outputDir}/delphes_events.\$(Process).root " # pythia8_events.\$(Process).hepmc.gz = ${outputDir}/pythia8_events.\$(Process).hepmc.gz ; 
fi


### Let the masses know what is going on
echo -e "\e[1;32m--> Preparing Submission... (${STAMP})\e[0m"
echo -e "\tGene Process: ${process}"
echo -e "\tParam Card:   ${param}"
echo -e "\tRun Card:     ${run}"
echo -e "\tDelphes Card: ${delphes}"
echo -e "\tJob Name:     ${jobName}"
echo -e "\tOutput Dir:   ${outputDir}"
echo -e "\tCondor Cfg:   ${subfile}"
echo -e "\tGridpack:     ${gridpackinput}"
echo "======================================================"

### Make submit folder, copy exe and start populating the condor configuration
mkdir -p ${outputDir}
### Don't think I need to do this copy...
cp ${exe} ${outputDir}

echo "universe = vanilla" > ${subfile}

totjobs=1
if [[ $5 != "" ]]; then
    totjobs=$5
fi

echo "executable = ${outputDir}/${exe}" >> ${subfile}
echo "Arguments = ${mg5BinPath} ${process} ${param} ${run} ${delphes} \$(Process) ${gridpackinput}" >> ${subfile}
echo "getenv = True" >> ${subfile}
echo "output = ${outputDir}/out.\$(Process).out" >> ${subfile}
echo "error  = ${outputDir}/out.\$(Process).err" >> ${subfile}
echo "Log    = ${outputDir}/out.\$(Process).log" >> ${subfile}
echo "should_transfer_files = YES" >> ${subfile}
echo "when_to_transfer_output = ON_EXIT" >> ${subfile}
### This is a bit of a mess...
if [[ $fullOutput == 1 ]]; then
    echo "transfer_output_files = ${jobName}.\$(Process).tar.gz,${gridpackoutput},hist.${jobName}.\$(Process).root" >> ${subfile}
    echo "transfer_output_remaps = \"${jobName}.\$(Process).tar.gz = ${outputDir}/${jobName}.\$(Process).tar.gz ; ${gridpackremap} ; hist.${jobName}.\$(Process).root = ${outputDir}/hist.${jobName}.\$(Process).root\"">> ${subfile}
else
    echo "transfer_output_files = hist.${jobName}.\$(Process).root" >> ${subfile}
    echo "transfer_output_remaps = \"hist.${jobName}.\$(Process).root = ${outputDir}/hist.${jobName}.\$(Process).root\"" >> ${subfile}
fi
echo "Queue ${totjobs}" >> ${subfile}
cat ${subfile}
echo "======================================================"
condor_submit -batch-name ${jobName} ${subfile}
echo ""
echo ""
