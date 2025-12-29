# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from .embedder import embedder
from .reranker import format_instruction, process_inputs, compute_logits

# Initialiser FastAPI
app = FastAPI(title="Encoding Service", version="0.0.0")

class Input_embed(BaseModel):
    texts: list[str]
    type: Literal["query", "document"]

class Output_embed(BaseModel):
    embeddings: list[list[float]]

@app.post("/embed", response_model=Output_embed)
async def embed(data: Input_embed, batch_size: int = 8):
    
    if data.type == "query":
        embeddings = embedder.encode(
            data.texts,
            prompt_name = "query",
            convert_to_numpy=True,
            batch_size=batch_size
        )
    elif data.type == "document":
        embeddings = embedder.encode(
            data.texts,
            convert_to_numpy=True,
            batch_size=batch_size
        )
    
    return Output_embed(embeddings=embeddings.tolist())

class Input_rerank(BaseModel):
    query: str
    documents: list[str]

class Output_rerank(BaseModel):
    scores: list[float]

@app.post("/rerank", response_model=Output_rerank)
async def rank(data: Input_rerank):

    pairs = [format_instruction(data.query, doc) for doc in data.documents]
    inputs = process_inputs(pairs)
    scores = compute_logits(inputs)
    
    return Output_rerank(scores=scores)