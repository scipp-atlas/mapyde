#!/bin/bash
#set -e # exit when any command fails

version=$1
if [[ $1 == "" ]]; then
    version="2.4.3"
fi
    
doOldmssm=0
# force older mssm_v4 for older versions of MG
if [[ ${version} == "2.4.3" || ${version} == "2.3.3" ]]; then
    doOldmssm=1
fi
MGversion="madgraph-${version}"

params=Higgsino
mass=154
ecms=13
subproc="_n2c1p"
proccard=VBFSUSY_EWKQCD${subproc}

if [[ $doOldmssm == 1 ]]; then
    params=Higgsino_CMS_v4
    proccard=VBFSUSY_EWKQCD${subproc}_v4
fi

mmjj=500
mmjj_max=-1
seed=0

deltaeta=3.0
nevents=5000
cores=20
anascript="SimpleAna.py"
#anascript="Delphes2SA.py"

outdata=/data/users/${USER}/SUSY # change this to a good local area to store output files

./run_VBFSUSY_standalone.sh \
    -E ${ecms} \
    -M ${mass} \
    -P ${proccard} \
    -c ${cores} \
    -p ${params} \
    -N ${nevents} \
    -m ${mmjj} \
    -x ${mmjj_max} \
    -e ${deltaeta} \
    -d ${seed} \
    -C ${anascript} \
    -I ${MGversion} \
    -s "__${MGversion}" \
    -b ${outdata} \
    -D -A -T # skip everything except madgraph
