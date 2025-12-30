# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from datetime import datetime, timezone
import time
from vllm import SamplingParams
from .embedder import embedder
from .vllm import llm

# Initialiser FastAPI
app = FastAPI(title="Encoding Service", version="0.0.0")

class Input_embed(BaseModel):
    texts: list[str]
    type: Literal["query", "document"] = "document"

class Output_embed(BaseModel):
    embeddings: list[list[float]]

class Input_generate(BaseModel):
    model: str
    prompt: str
    format: Optional[Dict[str, Any]] = None
    stream: bool = False
    temperature: float = 1.0
    max_tokens: Optional[int] = 512
    top_p: Optional[float] = 0.9
    top_k: Optional[int] = 50

class Output_generate(BaseModel):
    model: str
    created_at: str
    response: str
    done: bool
    context: Optional[list[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class Input_chat(BaseModel):
    model: str
    messages: list[Message]
    format: Optional[Dict[str, Any]] = None
    stream: bool = False
    temperature: float = 1.0
    max_tokens: Optional[int] = 512
    top_p: Optional[float] = 0.9
    top_k: Optional[int] = 50

class Output_chat(BaseModel):
    model: str
    created_at: str
    message: Message
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None

@app.post("/api/embed", response_model=Output_embed)
async def embed(data: Input_embed, batch_size: int = 8):

    ### asymetric embedding - adapted to Qwen
    if data.type == "query":
        embeddings = embedder.encode(
            data.texts,
            prompt_name = "query",
            convert_to_numpy=True,
            batch_size=batch_size
        )
    else:
        embeddings = embedder.encode(
            data.texts,
            convert_to_numpy=True,
            batch_size=batch_size
        )

    return Output_embed(embeddings=embeddings.tolist())

@app.post("/api/generate", response_model=Output_generate)
async def generate(data: Input_generate):
    """Endpoint de génération compatible Ollama"""
    start_time = time.time()
    
    sampling_params = SamplingParams(
        temperature=data.temperature,
        max_tokens=data.max_tokens,
        top_p=data.top_p,
        top_k=data.top_k,
    )
    
    if data.format:
        sampling_params.guided_decoding_backend = "outlines"
        sampling_params.guided_json = data.format
    
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


@app.post("/api/chat", response_model=Output_chat)
async def chat(data: Input_chat):
    """
    Endpoint de chat compatible Ollama.
    Gère les conversations multi-tours avec historique.
    Utilise automatiquement le chat template du modèle.
    """
    start_time = time.time()
    
    # Convertir les messages au format attendu par le tokenizer
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in data.messages
    ]
    
    # Appliquer le chat template du modèle automatiquement
    tokenizer = llm.get_tokenizer()
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Configurer les paramètres de sampling
    sampling_params = SamplingParams(
        temperature=data.temperature,
        max_tokens=data.max_tokens,
        top_p=data.top_p,
        top_k=data.top_k,
    )
    
    # Ajouter le guided decoding si un format est fourni
    if data.format:
        sampling_params.guided_decoding_backend = "outlines"
        sampling_params.guided_json = data.format
    
    # Générer avec vLLM
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
                "modified_at": datetime.now(timezone.utc).isoformat(),
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