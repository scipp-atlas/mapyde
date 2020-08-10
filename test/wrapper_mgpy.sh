#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}
base=${PWD}
datadir=output/${tag}

./scripts/mg5creator.py \
       -P cards/process/charginos \
       -r cards/run/default_LO.dat \
       -p cards/param/Higgsino.slha \
       -y cards/pythia/pythia8_card.dat \
       -m MN1 150.0 -m MN2 155.0 -m MC1 155.0 \
       -R ptj 20 -R etaj 4.5 \
       -E 100000 \
       -n 1000 \
       -t ${tag}

docker run \
       --rm \
       -v ${base}/cards:/cards \
       -v ${base}/${datadir}:/data \
       -w /output \
       gitlab-registry.cern.ch/scipp/mario-mapyde/madgraph:master \
       "mg5_aMC /data/run.mg5 && rsync -rav PROC_madgraph /data/madgraph"

