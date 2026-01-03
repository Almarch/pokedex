import requests
from .config import config
from urllib.parse import urljoin
from typing import Literal
from pydantic import BaseModel

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
    model = config["ollama"]["llm"],
):
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

def typed_gen(prompt, format, model = None):
    res = generate(
            prompt = prompt,
            format = format.model_json_schema(),
            **({"model": model} if model else {}),
        )

    return format.model_validate_json(res)

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

class Relevance(BaseModel):
    relevance: Literal[0, 1, 2, 3]

def rerank(
    query,
    documents,
):
    scores = []
    for doc in documents:

        prompt = f"""
### INSTRUCTIONS

You must assess the relevance of a document to address a given query.

Output a JSON: {{"relevance": 0 | 1 | 2 | 3}}
with the relevancy score as:

- 0: the document is very irrelevant
- 1: the document is a little bit irrelevant
- 2: the document is a little bit relevant
- 3: the document is very relevant

### QUERY

{query}

### DOCUMENT

{doc}
"""
        scores.append(
            typed_gen(
                prompt,
                Relevance,
                model = config["ollama"]["reranking"],
            )
        )
    return int(scores)