"""
Top-level entrypoint for the command line interface.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

import typer
from trogon import Trogon

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


PrefixOrNone = Optional[Prefix]


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Print the current version."),
    prefix: PrefixOrNone = typer.Option(
        None, help="Print the path prefix for data files."
    ),
    tui: bool = typer.Option(False, "--tui", help="Open Textual TUI."),
) -> None:
    """
    Manage top-level options
    """
    if version:
        typer.echo(f"mapyde v{mapyde.__version__}")
        raise typer.Exit()
    if prefix:
        typer.echo(getattr(mapyde.prefix, prefix.value).resolve())
        raise typer.Exit()
    if tui:
        Trogon(ctx.command, app_name=ctx.info_name, click_context=ctx).run()
        ctx.exit()


# for generating documentation using mkdocs-click
typer_click_object = typer.main.get_command(app)
