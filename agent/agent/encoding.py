import requests
from .config import config

def embed(
    prompt,
    type
):
    response = requests.post(
        config["encoding"]["url"] + "/encode",
        json = {
            "prompt": prompt,
            "type": type,
        }
    )
    return response.json()["vector"]


