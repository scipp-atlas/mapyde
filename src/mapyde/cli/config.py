import typer
from mapyde.utils import load_config, build_config
from mapyde.backends import madgraph
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


@app.command()
def generate_mg5(filename: str):
    user = load_config(filename)
    config = build_config(user)

    madgraph.generate_mg5config(config)
