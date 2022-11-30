See the [Scikit-HEP Developer introduction][skhep-dev-intro] for a detailed
description of best practices for developing Scikit-HEP packages.

[skhep-dev-intro]: https://scikit-hep.org/developer/intro

# Quick development

The fastest way to start with development is to use pipx and hatch. If you don't
have pipx, you can use `pipx run hatch` to run it without installing, or
`pipx install hatch`. If you don't have pipx (pip for applications), then you
can install with with `pip install pipx` (the only case were installing an
application with regular pip is reasonable). If you use macOS, then pipx and
hatch are both in brew, use `brew install pipx hatch`.

To use, run `hatch run dev:test`. This will test using every installed version
of Python on your system, skipping ones that are not installed. You can also run
specific jobs:

```console
$ hatch run lint  # Lint only
$ hatch run +py=3.9 dev:test  # Python 3.9 tests only
$ hatch run dev:py3.9:test  # Python 3.9 tests only
$ hatch run docs:serve  # Build and serve the docs
$ hatch run build  # Make an SDist and wheel
```

hatch handles everything for you, including setting up an temporary virtual
environment for each run.

# Setting up a development environment manually

You can set up a development environment by running:

```bash
python3 -m venv .venv
source ./.venv/bin/activate
pip install -v -e .[dev]
```

If you have the
[Python Launcher for Unix](https://github.com/brettcannon/python-launcher), you
can instead do:

```bash
py -m venv .venv
py -m install -v -e .[dev]
```

# Post setup

You should prepare pre-commit, which will help you by checking that commits pass
required checks:

```bash
pip install pre-commit # or brew install pre-commit on macOS
pre-commit install # Will install a pre-commit hook into the git repo
```

You can also/alternatively run `pre-commit run` (changes only) or
`pre-commit run --all-files` to check even without installing the hook.

# Testing

Use pytest to run the unit checks:

```bash
pytest
```

# Building docs

You can build the docs using:

```bash
hatch run docs:build
```

You can see a preview with:

```bash
hatch run docs:serve
```

# Pre-commit

This project uses pre-commit for all style checking. While you can run it with
hatch, this is such an important tool that it deserves to be installed on its
own. Install pre-commit and run:

```bash
pre-commit run -a
```

to check all files.
