import yaml
import importlib.resources as resources

with resources.open_text("encoding", "config.yaml") as f:
    config = yaml.safe_load(f)