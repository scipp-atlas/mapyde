"""
Command line interface for config
"""

from __future__ import annotations

import json

import typer

from mapyde.backends import madgraph
from mapyde.utils import build_config, load_config

app = typer.Typer()


@app.command()
def parse(filename: str) -> None:
    """
    Parse the configuration file and print to screen.
    """
    user = load_config(filename)
    config = build_config(user)

    typer.echo(json.dumps(config, indent=4))


@app.command()
def generate_mg5(filename: str) -> None:
    """
    Generate the madgraph configurations and write to local disk.
    """
    user = load_config(filename)
    config = build_config(user)

    madgraph.generate_mg5config(config)
