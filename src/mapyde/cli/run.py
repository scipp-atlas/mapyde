from __future__ import annotations
import typer
from mapyde.utils import load_config, build_config
from mapyde.runner import run_madgraph, run_delphes, run_ana, run_pyhf


app = typer.Typer()


def loadfile(filename: str):
    user = load_config(filename)
    config = build_config(user)
    return config


@app.command()
def all(filename: str):
    config = loadfile(filename)
    run_madgraph(config)
    run_delphes(config)
    run_ana(config)
    run_pyhf(config)


@app.command()
def madgraph(filename: str):
    config = loadfile(filename)
    run_madgraph(config)


@app.command()
def delphes(filename: str):
    config = loadfile(filename)
    run_delphes(config)


@app.command()
def analysis(filename: str):
    config = loadfile(filename)
    run_ana(config)


@app.command()
def pyhf(filename: str):
    config = loadfile(filename)
    run_pyhf(config)

