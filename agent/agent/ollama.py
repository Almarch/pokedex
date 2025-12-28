import requests
from .config import config

def generate(
    prompt,
    format = None,
    temperature = 0,
):
    response = requests.post(
        config["ollama"]["url"] + "/api/generate",
        json = {
            "model": config["ollama"]["llm"]["model"],
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

