import requests
from .config import config
from urllib.parse import urljoin

def embed(
    texts,
    type
):
    response = requests.post(
        urljoin(config["encoding"]["url"], "embed"),
        json = {
            "texts": texts,
            "type": type,
        }
    )
    return response.json()["embeddings"]

def rerank():
    pass


