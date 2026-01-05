from .config import config
from urllib.parse import urljoin
import json
import httpx

async def pull() -> None:
    async with httpx.AsyncClient() as client:
        for model in [
            config["ollama"]["llm"],
            config["ollama"]["embedding"],
            config["ollama"]["reranking"],
        ]:
            await client.post(
                urljoin(config["ollama"]["url"], "api/pull"),
                json= {
                    "name": model,
                },
            )

async def generate(
        prompt: str,
        format: type = None,
        temperature: float = 0,
        model: str = config["ollama"]["llm"],
    ) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            urljoin(config["ollama"]["url"], "api/generate"),
            json = {
                "model": model,
                "prompt": prompt,
                "format": format,
                "stream": False,
                "temperature": temperature,
            },
            timeout = None,
        )
    return response.json()["response"]

async def typed_gen(
        prompt: str,
        format: type,
        model: str = None
    ) -> dict:
    res = await generate(
            prompt = prompt,
            format = format.model_json_schema(),
            **({"model": model} if model else {}),
        )

    return json.loads(res)

async def embed(
        prompt: str,
    ) -> list[float]:
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            config["ollama"]["url"] + "/api/embeddings",
            json = {
                "model": config["ollama"]["embedding"],
                "prompt": prompt,
            }
        )
    return response.json()["embedding"]

