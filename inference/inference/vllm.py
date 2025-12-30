from vllm import LLM
from .config import config

llm = LLM(
    model=config["llm"]["model"],
    download_dir=config["cache"],
    quantization="awq",  # q4
    trust_remote_code=True,
    gpu_memory_utilization=0.9,
)