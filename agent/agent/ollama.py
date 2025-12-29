import requests
from .config import config
from urllib.parse import urljoin

def pull():
    response = requests.post(
        urljoin(config["ollama"]["url"], "api/pull"),
        json= {
            "name": config["ollama"]["model"]
        },
        stream=True
    )

    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))

def generate(
    prompt,
    format = None,
    temperature = 0,
):
    response = requests.post(
        urljoin(config["ollama"]["url"], "api/generate"),
        json = {
            "model": config["ollama"]["model"],
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

