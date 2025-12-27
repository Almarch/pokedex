from qdrant_client.models import Filter, FieldCondition, MatchValue
from .qdrant import qdrant
from .ollama import embed

def vector_search(query, language, n=10):
    query = embed(query)
    rag = qdrant.query_points(
        collection_name= f"description_{language}",
        query = query,
        limit = n
    )
    rag = [point.payload for point in rag.points]
    return rag

def name_search(names, language):
    rag, _ = qdrant.scroll(
        collection_name=f"description_{language}",
        scroll_filter=Filter(
            should=[
                FieldCondition(
                    key="name",
                    match=MatchValue(value=name)
                )
                for name in names
            ]
        ),
        with_payload=True,
        with_vectors=False
    )
    rag = [point.payload for point in rag]
    return rag