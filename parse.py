from jinja2 import Environment, FileSystemLoader, Template
import toml
import os

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a

def env_override(value, key):
    return os.getenv(key, value)

def get_defaults():
  env = Environment(loader=FileSystemLoader("./templates"))
  env.filters['env_override'] = env_override

  return env.get_template("defaults.toml")

import typer
def main(filename: str):
    tpl_defaults = get_defaults()
    defaults = toml.load(open(tpl_defaults.filename))

    env = Environment(loader=FileSystemLoader("."))
    env.filters['env_override'] = env_override

    tpl_user = env.get_template(filename)
    user = toml.load(open(tpl_user.filename))

    variables = merge(defaults, user)
    tpl_config = Template(toml.dumps(variables))
    config = toml.loads(tpl_config.render(PWD=os.getenv('PWD'), USER=os.getenv('USER'), **variables))

    import json
    typer.echo(json.dumps(config, indent=4))

if __name__ == "__main__":
    typer.run(main)

