"""
Top-level entrypoint for the command line interface.
"""
from __future__ import annotations

import typer

from mapyde.cli import config, run

app = typer.Typer()
app.add_typer(config.app, name="config")
app.add_typer(run.app, name="run")
