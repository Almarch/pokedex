from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, timezone
from .embedder import embedder, embed
from .reranker import rerank
from .llm import (
    llm, tokenizer, generate,
    stream_generate, stream_chat,
    parameterize_sampling, model,
    BaseInputGen, BaseOutputGen, Message
)

app = FastAPI(title="Inference service", version="0.0.0")

class Input_embed(BaseModel):
    model: str = ""
    input: str | list[str]
    type: Literal["query", "document"] = "document"

class Output_embed(BaseModel):
    model: str
    embeddings: list[list[float]]

class Input_rerank(BaseModel):
    model: str = ""
    query: str
    docuuments: list[str]

class Output_rerank(BaseModel):
    model: str
    scores: list[float]

class Input_generate(BaseInputGen):
    prompt: str

class Input_chat(BaseInputGen):
    messages: list[Message]

class Output_generate(BaseOutputGen):
    response: str
    context: Optional[list[int]] = None

class Output_chat(BaseOutputGen):
    message: Message

@app.post("/api/embed", response_model=Output_embed)
async def embed_api(data: Input_embed):
    embeddings = embed(data)
    return Output_embed(
        model=data.model,
        embeddings=embeddings.tolist()
    )

@app.post("/api/rerank", response_model=Output_rerank)
async def rerank_api(data: Input_rerank):
    scores = rerank(data)
    return Output_rerank(
        model=data.model,
        scores=scores.tolist()
    )

@app.post("/api/generate")
async def generate_api(data: Input_generate):
    
    sampling_params = parameterize_sampling(data)

    # Streaming mode
    if data.stream:
        return StreamingResponse(
            stream_generate(data.prompt, data.model, sampling_params),
            media_type="application/x-ndjson"
        )
    
    # Non-streaming mode
    generated_text, duration_ns, eval_count = generate(data.prompt, sampling_params)
    
    return Output_generate(
        model=data.model,
        created_at=datetime.now(timezone.utc).isoformat(),
        response=generated_text,
        done=True,
        eval_count=eval_count,
        total_duration=duration_ns,
    )

@app.post("/api/chat")
async def chat_api(data: Input_chat):
    
    sampling_params = parameterize_sampling(data)
    
    # Streaming mode
    if data.stream:
        return StreamingResponse(
            stream_chat(data.messages, data.model, sampling_params),
            media_type="application/x-ndjson"
        )
    
    # Non-streaming mode
    prompt = tokenizer.apply_chat_template(
        data.messages,
        tokenize=False,
        add_generation_prompt=True
    )
    generated_text, duration_ns, eval_count = generate(prompt, sampling_params)
    
    return Output_chat(
        model=data.model,
        created_at=datetime.now(timezone.utc).isoformat(),
        message=Message(role="assistant", content=generated_text),
        done=True,
        eval_count=eval_count,
        total_duration=duration_ns,
    )

@app.get("/api/tags")
async def tags():
    return {
        "models": [
            {
                "name": model,
                "modified_at": '1996-02-27T00:00:00+00:00',
                "size": 0,
            }
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "embedder_loaded": embedder is not None,
        "llm_loaded": llm is not None,
    }