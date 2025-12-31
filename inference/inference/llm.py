from vllm import LLM, SamplingParams
from .config import config
import json
import time
from datetime import datetime, timezone
from typing import Dict
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal, AsyncIterator

llm = LLM(
    model=config["llm"]["model"],
    download_dir=config["cache"],
    quantization=config["llm"]["quantization"],
    trust_remote_code=True,
    gpu_memory_utilization=0.9,
)

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class BaseInputGen(BaseModel):
    model: str
    format: Optional[Dict[str, Any]] = None
    stream: bool = False
    temperature: float = config["llm"]["temperature"]
    max_tokens: Optional[int] = config["llm"]["max_tokens"]
    top_p: Optional[float] = config["llm"]["top_p"]
    top_k: Optional[int] = config["llm"]["top_k"]

class BaseOutput(BaseModel):
    model: str
    created_at: str
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None

tokenizer = llm.get_tokenizer()

def parameterize_sampling(data):
    sampling_params = SamplingParams(
        temperature=data.temperature,
        max_tokens=data.max_tokens,
        top_p=data.top_p,
        top_k=data.top_k,
    )
    if data.format:
        sampling_params.guided_decoding_backend = "outlines"
        sampling_params.guided_json = data.format
        
    return sampling_params

async def stream_generate(
    prompt: str,
    sampling_params: SamplingParams
) -> AsyncIterator[str]:
    
    start_time = time.time()
    
    # vLLM streaming
    results_generator = llm.generate([prompt], sampling_params, use_tqdm=False)
    
    for output in results_generator:
        if output.outputs:
            chunk = {
                "model": "Pokédex",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "response": output.outputs[0].text,
                "done": False
            }
            yield f"{json.dumps(chunk)}\n"
    
    # Final message
    duration_ns = int((time.time() - start_time) * 1e9)
    final_chunk = {
        "model": "Pokédex",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "response": "",
        "done": True,
        "total_duration": duration_ns
    }
    yield f"{json.dumps(final_chunk)}\n"

async def stream_chat(
    messages: Message,
    sampling_params: SamplingParams
) -> AsyncIterator[str]:

    start_time = time.time()
    
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # vLLM streaming
    results_generator = llm.generate([prompt], sampling_params, use_tqdm=False)
    
    for output in results_generator:
        if output.outputs:
            chunk = {
                "model": "Pokédex",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "message": {
                    "role": "assistant",
                    "content": output.outputs[0].text
                },
                "done": False
            }
            yield f"{json.dumps(chunk)}\n"
    
    # Final message
    duration_ns = int((time.time() - start_time) * 1e9)
    final_chunk = {
        "model": "Pokédex",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "message": {
            "role": "assistant",
            "content": ""
        },
        "done": True,
        "total_duration": duration_ns
    }
    yield f"{json.dumps(final_chunk)}\n"

