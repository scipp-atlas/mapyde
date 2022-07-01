import typer
from mapyde.utils import load_config, build_config
import json

app = typer.Typer()


@app.command()
def parse(filename: str):
    user = load_config(filename)
    config = build_config(user)

    typer.echo(json.dumps(config, indent=4))


@app.command()
def hello():
    typer.echo("world")
