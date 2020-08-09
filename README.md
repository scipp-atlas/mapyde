# MadGraph-Pythia-Delphes

Tools run inside the docker image provided by Dockerfile, but you can pull them from DockerHub:

```
docker pull mhance:madgraph/pythiainterface
docker pull mhance:delphes/001
```

The jobs will run in a dedicated `output/` area once you check out the code.  Each job gets its own `${tag}`.

## Running

For an example of how to run `MadGraph`, see [test/wrapper_mgpy.sh](./test/wrapper_mgpy.sh).

For an example of how to run `Delphes` (and a script to transform the Delphes output into flat ntuples), see [test/wrapper_delphes.sh](./test/wrapper_delphes.sh).

## To Do

* Collect the output of the job and store it somewhere
* Clean up MadGraph/Pythia leftovers
* Revisit `scripts/SimpleAna.py` for SUSY work
