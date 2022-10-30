# mario-mapyde v0.4.0

MaPyDe stands for MadGraph-Pythia-Delphes which is a utility that allows one to
run all of the various HEP toolings or chain them together and perform a quick
analysis with the results, such as running CERN ATLAS SimpleAnalysis or pyhf.

---

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]
[![ReadTheDocs][rtd-badge]][rtd-link]

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/scipp-atlas/mario-mapyde/workflows/CI/badge.svg
[actions-link]:             https://github.com/scipp-atlas/mario-mapyde/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/mapyde
[conda-link]:               https://github.com/conda-forge/mapyde-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/scipp-atlas/mario-mapyde/discussions
[gitter-badge]:             https://badges.gitter.im/https://github.com/scipp-atlas/mario-mapyde/community.svg
[gitter-link]:              https://gitter.im/https://github.com/scipp-atlas/mario-mapyde/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
[pypi-link]:                https://pypi.org/project/mapyde/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/mapyde
[pypi-version]:             https://badge.fury.io/py/mapyde.svg
[rtd-badge]:                https://readthedocs.org/projects/mapyde/badge/?version=latest
[rtd-link]:                 https://mapyde.readthedocs.io/en/latest/?badge=latest
[sk-badge]:                 https://scikit-hep.org/assets/images/Scikit--HEP-Project-blue.svg
<!-- prettier-ignore-end -->

## Docker Images

Docker images are made available in our
[container registry](../../../container_registry).

```
docker pull ghcr.io/scipp-atlas/mario-mapyde/madgraph
docker pull ghcr.io/scipp-atlas/mario-mapyde/delphes
docker pull ghcr.io/scipp-atlas/mario-mapyde/pyplotting
```

If you want to run on a machine with an NVidia GPU and use it for limit setting
with `pyhf`, then there's a container for that too:

```
docker pull ghcr.io/scipp-atlas/mario-mapyde/pyplotting-cuda
```

## Running

Everyone is centralized around the concept of providing a user configuration
file that references a template. By default,
[defaults.toml](./templates/defaults.toml) is used (if not specified). These
configuration files significantly control how to run or execute the various
steps in the chain of `mapyde`. Use the command line interface to get started:

```
# display the help
mapyde --help

# display the prefix path for data cards shipped with mapyde
mapyde --prefix cards

# parse and display the config
mapyde config parse user.toml

# run all steps
maypde run all user.toml

# run only madgraph
mapyde run madgraph user.toml

# display the help for running
mapyde run --help
```

## Configuration Details

There are a lot of different configuration options one can specify. For right
now, the user is asked to look at [defaults.toml](./templates/defaults.toml),
run `mapyde config parse user.toml`, open a
[discussion][github-discussions-link], or look at the source code.

### MadGraph

Produces a `hepmc` file. You can:

- specify process, param, and run cards
  - define particle masses in config file
  - define additional kinematic cuts to apply at parton level
- specify pythia card
- define center of mass energy

### Delphes

Run a parameterized detector simulation, outputting a `ROOT` file. You can:

- specify Delphes card

### Analysis

Analyze the Delphes output, which could be user-provided analysis code. There
are some scripts already provided for you:

- [scripts/Delphes2SA.py](./scripts/Delphes2SA.py) will make an ntuple that can
  be parsed by `SimpleAnalysis` for limit setting.
- [scripts/SimpleAna.py](./scripts/SimpleAna.py) will make a generic "flat"
  ntuple in a ROOT file.
- [scripts/muscan.py](./scripts/muscan.py) will use pyhf to perform a mu-scan
  and compute upper-limits for a public likelihood injected with results from
  `SimpleAnalysis`.
