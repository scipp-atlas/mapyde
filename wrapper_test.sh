tag=${1}

if [[ $tag == "" ]]; then
    tag="test_Higgsino_001"
fi

python mg5creator.py \
       -P ProcCards/VBFSUSY_short \
       -r RunCards/default_LO.dat \
       -p ParamCards/Higgsino.slha \
       -y PythiaCards/pythia8_card.dat \
       -m MN1 150.0 -m MN2 155.0 -m MC1 155.0 \
       -E 100000 \
       -n 1000 \
       -t ${tag}


docker run \
       --rm \
       -v $PWD:$PWD -w $PWD \
       mhance/madgraph:pythiainterface \
       "cd output/${tag} && mg5_aMC run.mg5"


