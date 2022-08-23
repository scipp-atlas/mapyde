"""
Command line interface for run
"""

from __future__ import annotations

import typing as T

import typer

from mapyde.runner import (
    run_ana,
    run_delphes,
    run_madgraph,
    run_pyhf,
    run_root2hdf5,
    run_sa2json,
    run_sherpa,
    run_simpleanalysis,
)
from mapyde.utils import build_config, load_config

app = typer.Typer()


def loadfile(filename: str) -> T.Any:
    """
    Helper function to load a configuration file in and build the config.
    """
    user = load_config(filename)
    config = build_config(user)
    return config


@app.command("all")
def run_all(filename: str) -> None:
    """
    Run madgraph, delphes, analysis, and pyhf.
    """
    config = loadfile(filename)
    run_madgraph(config)
    run_delphes(config)
    run_ana(config)
    run_simpleanalysis(config)
    run_sa2json(config)
    if not config["pyhf"]["skip"]:
        run_pyhf(config)


@app.command()
def madgraph(filename: str) -> None:
    """
    Run madgraph.
    """
    config = loadfile(filename)
    stdout, stderr = run_madgraph(config)
    typer.echo(stdout)
    typer.secho(stderr, fg=typer.colors.RED)


@app.command()
def sherpa(filename: str) -> None:
    """
    Run Sherpa.
    """
    config = loadfile(filename)
    stdout, stderr = run_sherpa(config)
    typer.echo(stdout)
    typer.secho(stderr, fg=typer.colors.RED)


@app.command()
def delphes(filename: str) -> None:
    """
    Run delphes.
    """
    config = loadfile(filename)
    run_delphes(config)


@app.command()
def analysis(filename: str) -> None:
    """
    Run analysis.
    """
    config = loadfile(filename)
    run_ana(config)


@app.command()
def simpleanalysis(filename: str) -> None:
    """
    Run simpleanalysis (ATLAS tool)
    """
    config = loadfile(filename)
    run_simpleanalysis(config)


@app.command()
def sa2json(filename: str) -> None:
    """
    Run sa2json.
    """
    config = loadfile(filename)
    run_sa2json(config)


@app.command()
def pyhf(filename: str) -> None:
    """
    Run pyhf.
    """
    config = loadfile(filename)
    run_pyhf(config)


@app.command()
def root2hdf5(filename: str) -> None:
    """
    Transform from .root to .hdf5 format.
    """
    config = loadfile(filename)
    run_root2hdf5(config)
