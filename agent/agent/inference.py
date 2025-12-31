import requests
from .config import config
from urllib.parse import urljoin

def generate(
    prompt,
    format = None,
    temperature = 0,
):
    response = requests.post(
        urljoin(config["inference"]["url"], "api/generate"),
        json = {
            "model": "",
            "prompt": prompt,
            "format": format,
            "stream": False,
            "temperature": temperature,
        }
    )
    return response.json()["response"]

def typed_gen(prompt, format):
    res = generate(
            prompt = prompt,
            format = format.model_json_schema(),
            temperature = 0,
        )

    return format.model_validate_json(res).output

def embed(
    input,
    type
):
    response = requests.post(
        urljoin(config["inference"]["url"], "api/embed"),
        json = {
            "model": "",
            "inputs": input,
            "type": type,
        }
    )
    return response.json()["embeddings"]

def rerank(query, documents):
    response = requests.post(
        urljoin(config["inference"]["url"], "api/rerank"),
        json = {
            "model": "",
            "query": query,
            "documents": documents,
        }
    )
    return response.json()["scores"]

