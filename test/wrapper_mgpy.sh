#!/bin/bash
set -e # exit when any command fails

tag=${1:-"test_Higgsino_001"}

./mg5creator.py \
       -P cards/process/charginos \
       -r cards/run/default_LO.dat \
       -p cards/param/Higgsino.slha \
       -y cards/pythia/pythia8_card.dat \
       -m MN1 150.0 -m MN2 155.0 -m MC1 155.0 \
       -E 100000 \
       -n 1000 \
       -t ${tag}

docker run \
       --rm \
       -v $PWD/output/${tag}:/input \
       -w /input \
       mhance/madgraph:pythiainterface_002 \
       "mg5_aMC run.mg5"
