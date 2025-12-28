# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from .config import config
from typing import Literal

# Load the model
embedder = SentenceTransformer(
    config["encoder"]["model"],
    cache_folder="/cache",
    trust_remote_code=True
)

# Initialiser FastAPI
app = FastAPI(title="Encoding Service", version="0.0.0")

class Input(BaseModel):
    prompt: str
    type: Literal["query", "document"]

class Output(BaseModel):
    vector: list[float]

@app.post("/embed", response_model=Output)

async def embed(data: Input):

    embedding = embedder.encode(
        data.prompt,
        prompt_name = data.type,
        convert_to_numpy=True
    )
    
    return Output(vector=embedding.tolist())
