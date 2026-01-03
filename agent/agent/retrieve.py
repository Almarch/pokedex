from qdrant_client.models import Filter, FieldCondition, MatchValue
from .qdrant import qdrant
from .ollama import embed

def vector_search(query, language, n=10):
    query = embed(query)
    docs = qdrant.query_points(
        collection_name= f"description_{language}",
        query = query,
        limit = n
    )
    docs = [{**point.payload, "qdrant_id": point.id} for point in docs.points]
    return docs

def name_search(names, language):
    docs, _ = qdrant.scroll(
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
    docs = [{**point.payload, "qdrant_id": point.id} for point in docs]
    return docs

def pokemon_synthese(data, language):
    templates = {
        "en": "{name} is a {type}. {description}",
        "fr": "{name} est un {type}. {description}",
        "es": "{name} es un {type}. {description}",
        "it": "{name} è un {type}. {description}",
        "de": "{name} ist ein {type}. {description}"
    }
    
    template = templates[language]
    return template.format(**data)