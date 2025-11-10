import yaml, requests

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def generate(
    prompt,
    format = None,
    temperature = 0,
):
    response = requests.post(
        urljoin(config["ollama"]["url"], "/api/generate"),
        json = {
            "model": config["ollama"]["llm"]["model"],
            "prompt": prompt,
            "format": format,
            "stream": False,
            "temperature": temperature,
        }
    )
    return response.json()["response"]

def embed(
    prompt,
):
    response = requests.post(
        OLLAMA + "/api/embeddings",
        json = {
            "model": ENCODER,
            "prompt": prompt,
        }
    )
    return response.json()["embedding"]

encoder_window = config["ollama"]["encoder"]["window"]

def typed_gen(prompt, format):
    res = generate(
            prompt = prompt,
            format = format.model_json_schema()
        )

    return format.model_validate_json(res).output

