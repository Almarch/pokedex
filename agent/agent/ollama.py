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
    topicality: Literal[0, 1, 2, 3]
    specificity: Literal[0, 1, 2, 3]
    clarity: Literal[0, 1, 2, 3]

def rerank(
    query,
    documents,
):
    scores = []
    for doc in documents:

        prompt = f"""
### INSTRUCTIONS

You must assess the relevance of a document to address a given query.

For more stable scoring, rate the document according to 3 aspects:

1. Topicality: How well the document is about the query.
2. Specificity: How specific and detailed the information is.
3. Clarity: How clear and direct the information is.

Output ONLY a JSON object with 3 scores (0-3) for these aspects, as:

{{
  "topicality": 0 | 1 | 2 | 3,
  "specificity": 0 | 1 | 2 | 3,
  "clarity": 0 | 1 | 2 | 3
}}

Do not explain your answer. Output ONLY JSON.

### QUERY

{query}

### DOCUMENT

{doc}
"""     
        score = typed_gen(
            prompt,
            Relevance,
            model = config["ollama"]["reranking"],
        )
        scores.append(score)
    return scores