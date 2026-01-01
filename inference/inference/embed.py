from sentence_transformers import SentenceTransformer
from .config import config

embedder = SentenceTransformer(
    config["embed"]["model"],
    cache_folder=config["cache"],
    trust_remote_code=True,
    device='cuda',
)

if config["embed"]["asymmetric"]:
    def embed(data, batch_size: int = config["embed"]["batch_size"]):
        texts = [data.input] if isinstance(data.input, str) else data.input
        if data.type == "query":
            embeddings = embedder.encode(
                texts,
                prompt_name = "query",
                convert_to_numpy=True,
                batch_size=batch_size
            )
        else:
            embeddings = embedder.encode(
                texts,
                convert_to_numpy=True,
                batch_size=batch_size
            )
        return embeddings
else:
    def embed(data, batch_size: int = config["embed"]["batch_size"]):
        texts = [data.input] if isinstance(data.input, str) else data.input
        embeddings = embedder.encode(
            texts,
            convert_to_numpy=True,
            batch_size=batch_size
        )
        return embeddings