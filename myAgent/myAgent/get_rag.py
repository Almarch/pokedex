from .qdrant import qdrant
from .ollama import embed

def get_rag(query, n=5):
    query = embed(query)
    rag = qdrant.query_points(
        collection_name="pokemons",
        query = query,
        limit = n
    )
    rag = str([rag.points[i].payload for i in range(len(rag.points))])
    return rag
