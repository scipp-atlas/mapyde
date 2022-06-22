from jinja2 import Environment, FileSystemLoader
import toml
import os

def env_override(value, key):
    return os.getenv(key, value)

env = Environment(loader=FileSystemLoader("./templates"))
env.filters['env_override'] = env_override

tpl_defaults = env.get_template("defaults.toml")
defaults = toml.load(open(tpl_defaults.filename))

data = toml.loads(tpl_defaults.render(PWD=os.getenv('PWD'), USER=os.getenv('USER'), **defaults))
import json
print(json.dumps(data))
