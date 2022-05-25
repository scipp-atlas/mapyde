#!/bin/bash
#set -e # exit when any command fails

version=$1
if [[ $1 == "" ]]; then
    version="2.4.3"
fi
    
MGversion="madgraph-${version}"

doOldmssm=1

# force older mssm_v4 for older versions of MG
if [[ ${MGversion} == "madgraph-2.4.3" ]]; then
    doOldmssm=1
fi

params=Higgsino
mass=152
ecms=13
proccard=VBFSUSY_EWKQCD_charginos

if [[ $doOldmssm == 1 ]]; then
    params=Higgsino_CMS_v4
    proccard=VBFSUSY_EWKQCD_charginos_v4
fi

mmjj=500
mmjj_max=-1
seed=0

deltaeta=3.0
nevents=5000
cores=20
anascript="SimpleAna.py"
#anascript="Delphes2SA.py"

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
    -D -A -T # skip everything except madgraph

