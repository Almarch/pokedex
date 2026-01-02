from .config import config
from vllm import LLM

model = config["llm"]["model"]

llm_params = {
    "model": config["llm"]["model"],
    "download_dir": config["cache"],
    "gpu_memory_utilization": config["llm"]["gpu_memory_utilization"],
    "max_model_len": config["llm"]["max_model_len"],
}

llm = LLM(**llm_params)
tokenizer = llm.get_tokenizer()
