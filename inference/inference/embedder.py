from sentence_transformers import SentenceTransformer
from .config import config

embedder = SentenceTransformer(
    config["embedding"]["model"],
    cache_folder=config["cache"],
    trust_remote_code=True,
    device='cuda',
)

if config["embedding"]["asymmetric"]:
    def embed(data, batch_size: int = config["embedding"]["batch_size"]):
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
        return embeddings
else:
    def embed(data, batch_size: int = config["embedding"]["batch_size"]):
        embeddings = embedder.encode(
            data.texts,
            convert_to_numpy=True,
            batch_size=batch_size
        )
        return embeddings