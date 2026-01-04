from qdrant_client.models import Filter, FieldCondition, MatchValue
from .qdrant import qdrant
from .ollama import embed
from .config import Languages, default_language

def vector_search(
        query: str, 
        language: Languages = default_language,
        n: int = 5
    ) -> list[dict]:

    query = embed(query)
    docs = qdrant.query_points(
        collection_name= f"description_{language}",
        query = query,
        limit = n
    )
    docs = [{**point.payload, "qdrant_id": point.id} for point in docs.points]
    return docs

def name_search(
        names,
        language: Languages = default_language,
    ) -> list[dict]:

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

def pokemon_synthese(
        data: dict,
        language: Languages = default_language,
    ) -> str:
    templates = {
        "en": "{name} is a {type}. {description}",
        "fr": "{name} est un {type}. {description}",
        "es": "{name} es un {type}. {description}",
        "it": "{name} è un {type}. {description}",
        "de": "{name} ist ein {type}. {description}"
    }
    
    template = templates[language]
    return template.format(**data)