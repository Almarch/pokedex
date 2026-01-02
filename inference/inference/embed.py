from sentence_transformers import SentenceTransformer
from .config import config

model = config["embed"]["model"]
batch_size = config["embed"]["batch_size"]

if config["embed"]["gpu"]:
    device = "cuda"
else:
    device = "cpu"

embedder = SentenceTransformer(
    model,
    cache_folder=config["cache"],
    trust_remote_code=True,
    device=device,
)

def embed(input):
    texts = [input] if isinstance(input, str) else input
    embeddings = embedder.encode(
        texts,
        convert_to_numpy=True,
        batch_size=batch_size,
    )
    return embeddings
