"""
Top-level entrypoint for the command line interface.
"""
from __future__ import annotations

import typing as T
from enum import Enum

import typer

import mapyde
from mapyde.cli import config, run

app = typer.Typer()
app.add_typer(config.app, name="config")
app.add_typer(run.app, name="run")


class Prefix(str, Enum):
    """
    Enum for allowed options for printing path prefixes
    """

    DATA = "data"
    CARDS = "cards"
    LIKELIHOODS = "likelihoods"
    SCRIPTS = "scripts"
    TEMPLATES = "templates"


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", help="Print the current version."),
    prefix: T.Optional[Prefix] = typer.Option(
        None, help="Print the path prefix for data files."
    ),
) -> None:
    """
    Manage top-level options
    """
    if version:
        typer.echo(f"mapyde v{mapyde.__version__}")
        raise typer.Exit()
    if prefix:
        typer.echo(
            {
                Prefix.DATA: mapyde.data,
                Prefix.CARDS: mapyde.cards,
                Prefix.LIKELIHOODS: mapyde.likelihoods,
                Prefix.SCRIPTS: mapyde.scripts,
                Prefix.TEMPLATES: mapyde.templates,
            }[prefix].resolve()
        )
        raise typer.Exit()
