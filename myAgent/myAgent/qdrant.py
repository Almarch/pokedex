import yaml
from qdrant_client import QdrantClient
from .config import config

qdrant = QdrantClient(url = config["qdrant"]["url"])