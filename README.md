## Docker Images

Docker images are made available in our [container registry](../../../container_registry).

```
docker pull gitlab-registry.cern.ch/scipp/mario-mapyde/madgraph:master
docker pull gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master
docker pull gitlab-registry.cern.ch/scipp/mario-mapyde/pyplotting:master
```

If you want to run on a machine with an NVidia GPU and use it for limit setting with `pyhf`, then there's a container for that too:

```
docker pull gitlab-registry.cern.ch/scipp/mario-mapyde/pyplotting-cuda
```

## Running

There are a few layers of scripts to factorize the different tasks.  A typical pipeline will look like:

1. Call [test/wrapper_mgpy.sh](./test/wrapper_mgpy.s) to run MadGraph+Pythia and produce a .hepmc file.  The script takes options to specify things like:
    - proc/param/run cards for MadGraph
        - includes specifying particle masses, and
	- any kinematic cuts to apply at parton level
    - pythia card
    - center of mass energy
    - number of cores to use for MadGraph and Pythia
2. Call [test/wrapper_delphes.sh](./test/wrapper_delphes.sh) to run Delphes, which is a parameterized detector simulation.   The output is a ROOT file.  The script takes arguments to specify things like:
    - Delphes card
3. Call something like [test/wrapper_ana.sh](./test/wrapper_ana.sh) to analyze the Delphes output.  Note that this script can run user-specified code:
    - [scripts/SimpleAna.py](./scripts/SimpleAna.py) will make a generic "flat" ntuple in a ROOT file.
    - [scripts/Delphes2SA.py](./scripts/Delphes2SA.py) will make an ntuple that can be parsed by `SimpleAnalysis` for limit setting.
4. If you want to run limits, then there are two additional steps:
    1. Run [test/wrapper_SimpleAnalysis.sh](./test/wrapper_SimpleAnalysis.sh) to analyze the output of `Delphes2SA.py` and make inputs for limit setting
    1. Run [test/wrapper_pyhf.sh](./test/wrapper_pyhf.sh) to plug the results from `SimpleAnalysis` into the public likelihood.

Each job gets its own `${tag}`, which is used to tell the various steps in the pipeline which data to operate on.

For an example of a full pipeline, see [run_VBFSUSY_standalone](run_VBFSUSY_standalone), which itself takes various options to help steer the work.



