import requests
from .config import config
from urllib.parse import urljoin

def embed(
    prompt,
    type
):
    response = requests.get(
        urljoin(config["encoding"]["url"], "embed"),
        json = {
            "prompt": prompt,
            "type": type,
        }
    )
    return response.json()["vector"]


