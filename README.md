
Tools run inside the docker image provided by Dockerfile, but you can pull it from DockerHub:

```
docker pull mhance:madgraph/pythiainterface
```

For an example of how to run madgraph, see ```test/wrapper_mgpy.sh```:

```
tag="test"

python mg5creator.py \
       -P ProcCards/charginos \
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
       mhance/madgraph:pythiainterface_002 \
       "cd output/${tag} && mg5_aMC run.mg5"
```

The jobs will run in a dedicated "output" area once you check out the code.  Each job gets its own tag.

To do:
* Collect the output of the job and store it somewhere
* Clean up MadGraph/Pythia leftovers
