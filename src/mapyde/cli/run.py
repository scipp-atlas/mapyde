import typer
from mapyde.runner import run_madgraph,run_delphes,run_ana,run_pyhf


app = typer.Typer()


def loadfile(filename: str):
  user = load_config(filename)
  config = build_config(user)
  return config

@app.command()
def all(filename: str):
  config=loadfile(filename)
  run_madgraph(config)
  run_delphes(config)
  run_ana(config)
  run_pyhf(config)
  pass

@app.command()
def madgraph(filename: str):
  config=loadfile(filename)
  run_madgraph(config)
  pass

@app.command()
def delphes(filename: str):
  config=loadfile(filename)
  run_delphes(config)
  pass

@app.command()
def analysis(filename: str):
  config=loadfile(filename)
  run_ana(config)
  pass

@app.command(filename: str)
def pyhf():
  config=loadfile(filename)
  run_pyhf(config)
  pass


#@app.command()
#def run(filename: str):
#    user = load_config(filename)
#    config = build_config(user)
#
#    runner(config)
