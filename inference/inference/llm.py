from .config import config
from vllm import LLM

# Paramètres communs
llm_params = {
    "model": config["llm"]["model"],
    "download_dir": config["cache"],
    "gpu_memory_utilization": config["llm"]["gpu_memory_utilization"],
}

# Ajouter quantization si demandée
if config["llm"]["quantized"]:
    llm_params["quantization"] = "bitsandbytes"

llm = LLM(**llm_params)
tokenizer = llm.get_tokenizer()