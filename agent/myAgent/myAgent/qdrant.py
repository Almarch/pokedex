import yaml
from qdrant_client import QdrantClient

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

qdrant = QdrantClient(url = config["qdrant"]["url"])