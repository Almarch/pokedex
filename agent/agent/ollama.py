import requests
from .config import config
from urllib.parse import urljoin
import json

def pull() -> None:
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
        prompt: str,
        format: type,
        temperature: float = 0,
        model: str = config["ollama"]["llm"],
    ) -> str:
    response = requests.post(
        urljoin(config["ollama"]["url"], "api/generate"),
        json = {
            "model": model,
            "prompt": prompt,
            "format": format,
            "stream": False,
            "temperature": temperature,
        }
    )
    return response.json()["response"]

def typed_gen(
        prompt: str,
        format: type,
        model: str = None
    ) -> dict:
    res = generate(
            prompt = prompt,
            format = format.model_json_schema(),
            **({"model": model} if model else {}),
        )

    return json.loads(res)

def embed(
        prompt: str,
    ) -> list[float]:
    
    response = requests.post(
        config["ollama"]["url"] + "/api/embeddings",
        json = {
            "model": config["ollama"]["embedding"],
            "prompt": prompt,
        }
    )
    return response.json()["embedding"]

