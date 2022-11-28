# Installation

---

## pip

mapyde is available on PyPI and can be installed with
[pip](https://pip.pypa.io).

```
pip install mapyde
```

<!-- prettier-ignore -->
!!! warning
    This method modifies the Python environment in which you choose to install. Consider instead using [pipx](#pipx) or virtual environments to avoid dependency conflicts.

## pipx

[pipx](https://github.com/pypa/pipx) allows for the global installation of
Python applications in isolated environments.

```
pipx install mapyde
```

## virtual environment

```
python -m venv venv
source venv/bin/activate
python -m pip install mapyde
```

## Conda

See the [feedstock](https://github.com/conda-forge/mapyde-feedstock) for more
details.

```
conda install -c conda-forge mapyde
```

or with [mamba](https://github.com/mamba-org/mamba):

```
mamba install mapyde
```

<!-- prettier-ignore -->
!!! warning
    This method modifies the Conda environment in which you choose to install. Consider instead using [pipx](#pipx) or [condax](https://github.com/mariusvniekerk/condax) to avoid dependency conflicts.
