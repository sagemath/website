# coding: utf8
import yaml
import os
from os.path import join, dirname

config = mirrors = packages = None

for name in ["config", "mirrors"]:
    fn = join(dirname(__file__), name) + ".yaml"
    data = yaml.load(open(fn), Loader=yaml.SafeLoader)
    globals()[name] = data

# Override Google Maps API key with environment variable if set
if config and "maps_api_key" in config:
    config["maps_api_key"] = os.environ.get("GOOGLE_MAPS_API_KEY", config["maps_api_key"])
