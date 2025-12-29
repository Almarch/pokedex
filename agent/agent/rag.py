from qdrant_client.models import Filter, FieldCondition, MatchValue
from .qdrant import qdrant
from .encoding import embed, rerank

def vector_search(query, language, n=20):
    query = embed([query], type = "query")[0]
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

def pokemon_synthese(data, language):
    templates = {
        "en": "{name} is a {type}. {description}",
        "fr": "{name} est un {type}. {description}",
        "es": "{name} es un {type}. {description}",
        "it": "{name} è un {type}. {description}",
        "de": "{name} ist ein {type}. {description}"
    }
    
    template = templates.get(language, templates["en"])
    return template.format(**data)


