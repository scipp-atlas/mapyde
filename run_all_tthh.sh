#!/bin/bash
#set -e # exit when any command fails

ecms=14

for proc in ttbbjj; do #ttbbz ttbbh tthh ttvv ttbbv ttbbbb ttbbcc ttbbjj; do
    #                                                      process E_CMS   jobs seed
    /export/home/mhance/mario-mapyde/submit_tthh_condor.sh ${proc} ${ecms} 1000 1000
done
