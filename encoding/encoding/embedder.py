from sentence_transformers import SentenceTransformer
from .config import config

embedder = SentenceTransformer(
    config["embedding"]["model"],
    cache_folder=config["cache"],
    trust_remote_code=True
)