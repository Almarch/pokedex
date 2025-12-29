# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from .config import config
from typing import Literal

# Load the model
embedder = SentenceTransformer(
    config["embedding"]["model"],
    cache_folder=config["cache"],
    trust_remote_code=True
)

# Initialiser FastAPI
app = FastAPI(title="Encoding Service", version="0.0.0")

class Input(BaseModel):
    prompt: str
    type: Literal["query", "document"]

class Output(BaseModel):
    vector: list[float]

@app.get("/embed", response_model=Output)
async def embed(data: Input):

    if data.type == "query":
        embedding = embedder.encode(
            data.prompt,
            prompt_name = "query",
            convert_to_numpy=True
        )
    elif data.type == "document":
        embedding = embedder.encode(
            data.prompt,
            convert_to_numpy=True
        )
    
    return Output(vector=embedding.tolist())
