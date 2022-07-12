from __future__ import annotations

import json

import typer

from mapyde.backends import madgraph
from mapyde.utils import build_config, load_config

app = typer.Typer()


@app.command()
def parse(filename: str) -> None:
    user = load_config(filename)
    config = build_config(user)

    typer.echo(json.dumps(config, indent=4))


@app.command()
def hello() -> None:
    typer.echo("world")


@app.command()
def generate_mg5(filename: str) -> None:
    user = load_config(filename)
    config = build_config(user)

    madgraph.generate_mg5config(config)
