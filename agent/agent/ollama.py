import requests
from .config import config
from urllib.parse import urljoin

def pull():
    for model in [
        config["ollama"]["llm"],
        config["ollama"]["embedding"],
        config["ollama"]["reranking"],
    ]:
        requests.post(
            urljoin(config["ollama"]["url"], "api/pull"),
            json= {
                "name": model,
            },
            stream=False
        )

def generate(
    prompt,
    format = None,
    temperature = 0,
):
    response = requests.post(
        urljoin(config["ollama"]["url"], "api/generate"),
        json = {
            "model": config["ollama"]["llm"],
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
            format = format.model_json_schema()
        )

    return format.model_validate_json(res).output

def embed(
    prompt,
):
    response = requests.post(
        config["ollama"]["url"] + "/api/embeddings",
        json = {
            "model": config["ollama"]["encoding"],
            "prompt": prompt,
        }
    )
    return response.json()["embedding"]
