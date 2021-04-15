#!/bin/bash
#set -e # exit when any command fails

ecms=14

for proc in tthh; do #tthh ttvv ttbbv ttbbbb ttbbcc ttbbjj; do
    /export/home/mhance/mario-mapyde/submit_tthh_condor.sh ${proc} ${ecms} 3
done

#for proc in ttbbjj ttbbz ttbbh; do #tthh ttvv ttbbv ttbbbb ttbbcc ttbbjj; do
#    run_tthh.sh ${proc} "sherpa"
#done
