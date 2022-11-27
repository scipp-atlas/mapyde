# mapyde

![SCIPP logo](assets/images/logo.svg){ align="left" width="300" role="img" }

|         |                                                                                                                                                                                                                                                                                            |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CI/CD   | [![CI - Test][actions-badge-ci]{ loading=lazy .off-glb }][actions-link-ci] [![CI - Docker][actions-badge-docker]{ loading=lazy .off-glb }][actions-link-docker]                                                                                                                            |
| Docs    | [![Docs - Release][actions-badge-docs]{ loading=lazy .off-glb }][actions-link-docs] [![Docs - Dev][actions-badge-docs-dev]{ loading=lazy .off-glb }][actions-link-docs-dev]                                                                                                                |
| Package | [![PyPI - Downloads][pypi-downloads]{ loading=lazy .off-glb }][pypi-link] [![PyPI - Version][pypi-version]{ loading=lazy .off-glb }][pypi-link] [![PyPI platforms][pypi-platforms]{ loading=lazy .off-glb }][pypi-link] [![Conda-Forge][conda-badge]{ loading=lazy .off-glb }][conda-link] |
| Meta    | [![GitHub - Discussion][github-discussions-badge]{ loading=lazy .off-glb }][github-discussions-link] [![GitHub - Issue][github-issues-badge]{ loading=lazy .off-glb }][github-issues-link] [![License - Apache 2.0][license-badge]{ loading=lazy .off-glb }][license-link]                 |

<!-- prettier-ignore-start -->
[actions-badge-ci]:         https://github.com/scipp-atlas/mario-mapyde/actions/workflows/ci.yml/badge.svg?branch=main
[actions-link-ci]:          https://github.com/scipp-atlas/mario-mapyde/actions/workflows/ci.yml
[actions-badge-docker]:     https://github.com/scipp-atlas/mario-mapyde/actions/workflows/docker.yml/badge.svg?branch=main
[actions-link-docker]:      https://github.com/scipp-atlas/mario-mapyde/actions/workflows/docker.yml
[actions-badge-docs]:       https://github.com/scipp-atlas/mario-mapyde/actions/workflows/docs-release.yml/badge.svg?branch=main
[actions-link-docs]:        https://github.com/scipp-atlas/mario-mapyde/actions/workflows/docs-release.yml
[actions-badge-docs-dev]:   https://github.com/scipp-atlas/mario-mapyde/actions/workflows/docs-dev.yml/badge.svg?branch=main
[actions-link-docs-dev]:    https://github.com/scipp-atlas/mario-mapyde/actions/workflows/docs-dev.yml
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/mapyde
[conda-link]:               https://github.com/conda-forge/mapyde-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/scipp-atlas/mario-mapyde/discussions
[github-issues-badge]:      https://img.shields.io/static/v1?label=Issues&message=File&color=blue&logo=github
[github-issues-link]:       https://github.com/scipp-atlas/mario-mapyde/issues
[pypi-link]:                https://pypi.org/project/mapyde/
[pypi-downloads]:           https://img.shields.io/pypi/dm/mapyde.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/mapyde
[pypi-version]:             https://badge.fury.io/py/mapyde.svg
[license-badge]:            https://img.shields.io/badge/License-Apache_2.0-blue.svg
[license-link]:             https://spdx.org/licenses/Apache-2.0.html
<!-- prettier-ignore-end -->

---

MaPyDe stands for MadGraph-Pythia-Delphes which is a utility that allows one to
run all of the various HEP toolings or chain them together and perform a quick
analysis with the results, such as running CERN ATLAS SimpleAnalysis or pyhf.

## Features

- Multiple backends supported
  - [x] docker
  - [x] singularity
  - [x] apptainer
- Easy configuration with sensible defaults
- Usable [CLI](cli/about.md) relying on a single config file

## License

mapyde is distributed under the terms of the [Apache 2.0][license-url] license.

## Navigation

Documentation for specific `MAJOR.MINOR` versions can be chosen by using the
dropdown on the top of every page. The `dev` version reflects changes that have
not yet been released.

Also, desktop readers can use special keyboard shortcuts:

| Keys                                                         | Action                          |
| ------------------------------------------------------------ | ------------------------------- |
| <ul><li><kbd>,</kbd> (comma)</li><li><kbd>p</kbd></li></ul>  | Navigate to the "previous" page |
| <ul><li><kbd>.</kbd> (period)</li><li><kbd>n</kbd></li></ul> | Navigate to the "next" page     |
| <ul><li><kbd>/</kbd></li><li><kbd>s</kbd></li></ul>          | Display the search modal        |
