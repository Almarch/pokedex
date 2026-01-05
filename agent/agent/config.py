import yaml
import importlib.resources as resources
from typing import Literal

with resources.open_text("agent", "config.yaml") as f:
    config = yaml.safe_load(f)

Languages = Literal[tuple(config["languages"]["supported"])]
default_language = config["languages"]["default"]