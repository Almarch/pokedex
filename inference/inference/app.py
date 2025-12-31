from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, timezone
import time
from .embedder import embedder, embed
from .llm import (
    llm, tokenizer,
    stream_generate, stream_chat,
    parameterize_sampling,
    BaseInputGen, BaseOutputGen, Message
)

# Initialiser FastAPI
app = FastAPI(title="Encoding Service", version="0.0.0")

class Input_embed(BaseModel):
    texts: list[str]
    type: Literal["query", "document"] = "document"

class Output_embed(BaseModel):
    embeddings: list[list[float]]

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
    return Output_embed(embeddings=embeddings.tolist())

@app.post("/api/generate")
async def generate_api(data: Input_generate):
    
    sampling_params = parameterize_sampling(data)

    if data.stream:
        return StreamingResponse(
            stream_generate(data.prompt, data.model, sampling_params),
            media_type="application/x-ndjson"
        )
    
    # non-streaming mode
    start_time = time.time()
    output = llm.generate([data.prompt], sampling_params)[0]
    generated_text = output.outputs[0].text
    duration_ns = int((time.time() - start_time) * 1e9)
    
    return Output_generate(
        model=data.model,
        created_at=datetime.now(timezone.utc).isoformat(),
        response=generated_text,
        done=True,
        eval_count=len(output.outputs[0].token_ids),
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
    start_time = time.time()
    prompt = tokenizer.apply_chat_template(
        data.messages,
        tokenize=False,
        add_generation_prompt=True
    )
    output = llm.generate([prompt], sampling_params)[0]
    generated_text = output.outputs[0].text.strip()
    duration_ns = int((time.time() - start_time) * 1e9)
    
    return Output_chat(
        model=data.model,
        created_at=datetime.now(timezone.utc).isoformat(),
        message=Message(role="assistant", content=generated_text),
        done=True,
        eval_count=len(output.outputs[0].token_ids),
        total_duration=duration_ns,
    )

@app.get("/api/tags")
async def tags():
    return {
        "models": [
            {
                "name": "Pokédex",
                "modified_at": '2000-01-01T00:00:00+00:00',
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